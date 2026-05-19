from typing import List, Tuple, Dict
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
import re


class BM25Retriever:
    """BM25 lexical retrieval for hybrid search."""
    
    def __init__(self, documents: List[Document]):
        """Initialize BM25 with documents."""
        self.documents = documents
        
        # Tokenize documents
        self.tokenized_docs = [self._tokenize(doc.page_content) for doc in documents]
        
        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_docs)
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple tokenization."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split on whitespace and filter empty tokens
        tokens = [t for t in text.split() if t and len(t) > 1]
        return tokens
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search using BM25 scoring."""
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:k]
        
        # Return documents with scores
        results = [
            (self.documents[i], float(scores[i])) 
            for i in top_indices 
            if scores[i] > 0
        ]
        
        return results


def hybrid_search(
    vector_docs: List[Tuple[Document, float]],
    bm25_docs: List[Tuple[Document, float]],
    alpha: float = 0.5,
    k: int = 5
) -> List[Tuple[Document, float]]:
    """
    Combine vector and BM25 results using weighted sum.
    alpha: weight for vector search (1-alpha for BM25)
    """
    # Normalize scores to 0-1 range
    vector_scores = {doc.metadata.get('source_index', id(doc)): score for doc, score in vector_docs}
    bm25_scores = {doc.metadata.get('source_index', id(doc)): score for doc, score in bm25_docs}
    
    # Combine documents
    all_docs = {}
    
    for doc, score in vector_docs:
        doc_id = id(doc)
        all_docs[doc_id] = {'doc': doc, 'vector_score': score, 'bm25_score': 0}
    
    for doc, score in bm25_docs:
        doc_id = id(doc)
        if doc_id in all_docs:
            all_docs[doc_id]['bm25_score'] = score
        else:
            all_docs[doc_id] = {'doc': doc, 'vector_score': 0, 'bm25_score': score}
    
    # Calculate hybrid scores
    hybrid_results = []
    for doc_id, data in all_docs.items():
        # Normalize and combine
        vector_norm = data['vector_score'] / max([d['vector_score'] for d in all_docs.values()]) if any(d['vector_score'] for d in all_docs.values()) else 0
        bm25_norm = data['bm25_score'] / max([d['bm25_score'] for d in all_docs.values()]) if any(d['bm25_score'] for d in all_docs.values()) else 0
        
        hybrid_score = alpha * vector_norm + (1 - alpha) * bm25_norm
        hybrid_results.append((data['doc'], hybrid_score))
    
    # Sort by hybrid score
    hybrid_results.sort(key=lambda x: x[1], reverse=True)
    
    return hybrid_results[:k]
