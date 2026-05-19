# Advanced RAG Architecture & Implementation Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Query Rewriter                               │
│  - Expands query to multiple variants                           │
│  - Generates synonyms and related terms                         │
│  - Breaks down complex queries                                  │
└────────────┬──────────────────────────────┬──────────────────────┘
             │                              │
             ▼                              ▼
     Multiple Queries        Alternative Phrasings
             │                              │
    ┌────────┴──────────────┬───────────────┴──────────┐
    │                       │                          │
    ▼                       ▼                          ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│Vector Search │  │BM25 Search   │  │Vector Search (alt)   │
│(Semantic)    │  │(Lexical)     │  │                      │
│Embedding DB  │  │Index         │  │                      │
└──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘
       │                 │                     │
       └─────────────────┼─────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Hybrid Score Combination      │
        │  (α=0.6 vector, 0.4 lexical)   │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │   Metadata Filtering           │
        │   (page, source, date, etc)    │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │    Reranking                   │
        │  - CrossEncoder (primary)      │
        │  - Keyword overlap (fallback)  │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │   Contextual Compression       │
        │   (extract key portions)       │
        │   [Optional]                   │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │   Deduplication &              │
        │   Format for LLM Context       │
        └──────────────┬─────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │   Final Context with Sources   │
        │   (ranked, annotated)          │
        └────────────────────────────────┘
                       │
                       ▼
        ┌────────────────────────────────┐
        │   LLM Chat Generation          │
        │   (with system prompts)        │
        └────────────────────────────────┘
```

## Component Details

### 1. Query Rewriter (`app/rag/query_rewriter.py`)

**Purpose**: Transform single query into multiple variants
**Methods**:
- `rewrite_query()`: Uses LLM to generate 3-5 variants
- `decompose_query()`: Simple rule-based decomposition

**Why**: Different phrasings capture different document perspectives
- "machine learning" vs "What is ML?"
- Catches both exact and semantic matches

### 2. Vector Search (LangChain + Chroma)

**What it does**: 
- Embeds query and documents using Sentence-Transformers
- Computes semantic similarity
- Returns top-k closest vectors

**Advantage**: Understands meaning and context

### 3. BM25 Hybrid Search (`app/rag/bm25_retriever.py`)

**What it does**:
- Tokenizes query and documents
- Scores based on term frequency + inverse document frequency
- Fast, deterministic scoring

**Advantage**: Exact keyword matching, good for technical docs

### 4. Hybrid Score Combination

**Formula**: `hybrid_score = α × vector_score + (1-α) × bm25_score`
- α = 0.6 (60% semantic, 40% keyword)
- Combines strengths of both approaches
- Balanced coverage of different search types

### 5. Metadata Filtering

**Supported Filters**:
- `page`: Document page number
- `source`: Document file name
- `chunk_id`: Chunk identifier
- `custom`: Any metadata in document

**Example**:
```python
metadata_filter={"page": 0, "source": "report.pdf"}
```

### 6. Reranking (`app/rag/reranker.py`)

**Primary: Cross-Encoder**
- Considers full query + document pairs
- More accurate than vector similarity alone
- Uses `cross-encoder/ms-marco-MiniLM-L-12-v2`

**Fallback: Simple Reranking**
- Keyword overlap scoring
- Metadata-based boost
- Used when cross-encoder unavailable

**Impact**: Typically improves top-5 relevance by 20-30%

### 7. Contextual Compression (`app/rag/contextual_compression.py`)

**What it does**:
- Extracts only query-relevant portions of documents
- Removes redundant information
- Reduces token count for LLM

**When to use**:
- Documents are large (>2000 tokens)
- Cost/latency is critical
- Want focused context

### 8. Semantic Chunking (`app/rag/pdf_loader.py`)

**Process**:
1. Split PDF into pages
2. Extract sentences (semantic boundaries)
3. Group sentences into coherent chunks
4. Add metadata (source, page, chunk_id)

**Advantage**: Preserves paragraph structure and meaning

### 9. Sliding Window Retrieval

**Process**:
1. Create chunks with overlap
2. Each chunk contains context from neighbors
3. Better for sequential content

**Function**: `load_and_split_pdf_with_sliding_window()`

## Data Flow

### Initialization
```
Document Upload
    ↓
PDF Loader (Semantic Chunking)
    ↓
Store in Vector DB (Chroma)
    ↓
Index in BM25
    ↓
Ready for Retrieval
```

### Query Retrieval
```
User Query
    ↓
Query Rewriter (generate variants)
    ↓
Parallel:
  - Vector search (all variants)
  - BM25 search (all variants)
    ↓
Combine & Deduplicate
    ↓
Filter by Metadata
    ↓
Rerank with Cross-Encoder
    ↓
Optionally Compress
    ↓
Format Context
    ↓
Pass to LLM
```

## Configuration Options

### Retriever Configuration

```python
retrieve_advanced_context(
    conversation_id=1,
    query="user query",
    k=5,                          # Number of results
    metadata_filter=None,         # Optional filtering
    use_multi_query=True,         # Enable query expansion
    use_reranking=True,           # Enable cross-encoder
    use_compression=False,        # Compress snippets
    provider="openrouter"         # LLM for query rewriting
)
```

### Hybrid Search Weights

```python
alpha = 0.6  # Vector search weight
        # 1-alpha = BM25 weight
```

### Reranker Selection

```python
# Auto-selects best available:
# 1. CrossEncoder (if sentence-transformers available)
# 2. SimpleReranker (keyword + metadata)
```

## Performance Considerations

### Speed Optimization
- `use_multi_query=False`: Faster (single query only)
- `use_reranking=True`: Minimal overhead (typically <100ms)
- `use_compression=False`: Faster (skip LLM call)

### Quality Optimization
- `use_multi_query=True`: Better coverage
- `use_reranking=True`: Better ranking
- `use_compression=True`: Cleaner context

### Default Balancing
- All strategies enabled by default
- Graceful degradation if components fail
- Automatic fallback to basic retrieval

## Error Handling

```python
try:
    # Try advanced retrieval
    context = retrieve_context(use_advanced=True)
except Exception as e:
    logger.warning(f"Advanced failed: {e}")
    # Fallback to basic
    context = retrieve_context(use_advanced=False)
```

## Logging

All components log to `app.core.logging`:
- INFO: Strategy selections
- WARNING: Fallback events
- ERROR: Critical failures

## Integration Points

### In Chat Service
```python
# app/services/chat_service.py automatically uses:
rag_context = retrieve_context(
    conversation_id,
    message,
    use_advanced=True  # ← Always advanced
)
```

### Direct Usage
```python
from app.rag.retriever import retrieve_context

context = retrieve_context(
    conversation_id=1,
    query="What is the summary?",
    use_advanced=True
)
```

## Testing

Use provided examples in `ADVANCED_RAG_EXAMPLES.py`:
```bash
python -m app.rag.ADVANCED_RAG_EXAMPLES
```

## Future Enhancements

1. **Dynamic α tuning**: Learn best hybrid weights from feedback
2. **Query caching**: Cache results for frequent queries
3. **Active learning**: Improve based on user feedback
4. **Graph retrieval**: Use knowledge graphs for connections
5. **Re-ranking learning**: Train custom reranker on your data
6. **Caching layer**: Redis/Memcached for speed

## Troubleshooting

### "Advanced retrieval failed, falling back"
- Check logs for specific error
- Verify vector DB has documents
- Ensure LLM provider keys are configured

### Slow retrieval
- Disable `use_compression`
- Disable `use_multi_query`
- Reduce `k` parameter

### Poor result quality
- Enable `use_reranking=True`
- Enable `use_multi_query=True`
- Check document chunking (semantic vs basic)

### Out of memory
- Reduce `k` parameter
- Enable `use_compression=True`
- Use basic retrieval `use_advanced=False`
