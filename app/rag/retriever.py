from app.rag.vectordb import load_vector_store
from app.rag.advanced_retriever import retrieve_advanced_context
from app.core.logging import logger


def _distance_to_relevance(distance):
    try:
        distance = float(distance)
    except (TypeError, ValueError):
        return 0.0

    if distance < 0:
        return 0.0

    return 1.0 / (1.0 + distance)


def retrieve_context(
    conversation_id: int,
    query: str,
    k: int = 5,
    min_score: float = 0.15,
    use_advanced: bool = True
):
    """
    Retrieve context from RAG system.
    
    Args:
        conversation_id: ID of conversation
        query: User query
        k: Number of results
        min_score: Minimum relevance threshold
        use_advanced: Use advanced RAG strategies (default: True)
    """
    if use_advanced:
        # Use advanced retrieval with all strategies
        try:
            return retrieve_advanced_context(
                conversation_id,
                query,
                k=k,
                use_all_strategies=True
            )
        except Exception as e:
            logger.warning(f"Advanced retrieval failed: {e}, falling back to basic")
            return retrieve_context_basic(conversation_id, query, k, min_score)
    else:
        # Fallback to basic vector retrieval
        return retrieve_context_basic(conversation_id, query, k, min_score)


def retrieve_context_basic(
    conversation_id: int,
    query: str,
    k: int = 5,
    min_score: float = 0.15
):
    """
    Basic vector similarity retrieval (legacy).
    Used as fallback when advanced strategies are disabled.
    """
    vectordb = load_vector_store(conversation_id)

    if vectordb is None:
        return ""

    docs_with_scores = vectordb.similarity_search_with_score(
        query,
        k=k
    )

    if not docs_with_scores:
        return ""

    scored_docs = []
    for doc, score in docs_with_scores:
        relevance = _distance_to_relevance(score)
        if relevance >= min_score:
            scored_docs.append((doc, relevance))

    if not scored_docs:
        return ""

    scored_docs.sort(key=lambda item: item[1], reverse=True)

    context_segments = []
    source_labels = []
    for idx, (doc, relevance) in enumerate(scored_docs, start=1):
        source = doc.metadata.get("source", "unknown source")
        page = doc.metadata.get("page")
        chunk_id = doc.metadata.get("chunk_id")

        source_label = source
        if page is not None:
            source_label += f" | page {page}"
        if chunk_id is not None:
            source_label += f" | chunk {chunk_id}"

        source_labels.append(source_label)
        context_segments.append(
            f"Source {idx}: {source_label} (relevance={relevance:.4f})\n{doc.page_content.strip()}"
        )

    top_sources = ", ".join(source_labels[:3])
    header = f"Top candidate sources: {top_sources}" if top_sources else "Relevant document context:"

    return header + "\n\n" + "\n\n".join(context_segments)
