from typing import List, Tuple
from langchain_core.documents import Document


class CrossEncoderReranker:
    """Reranks documents using a cross-encoder model."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """Initialize reranker with cross-encoder model."""
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
        except Exception as e:
            print(f"Failed to load cross-encoder: {e}. Reranking disabled.")
            self.model = None
    
    def rerank(
        self, 
        query: str,
        documents: List[Document],
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on relevance to query.
        Returns top-k documents with reranking scores.
        """
        if not self.model or not documents:
            # Fallback: return documents with dummy scores
            return [(doc, 0.5) for doc in documents[:top_k]]
        
        try:
            # Prepare pairs for cross-encoder
            pairs = [[query, doc.page_content] for doc in documents]
            
            # Get scores
            scores = self.model.predict(pairs)
            
            # Combine documents with scores
            ranked = list(zip(documents, scores))
            
            # Sort by score descending
            ranked.sort(key=lambda x: x[1], reverse=True)
            
            return ranked[:top_k]
        
        except Exception as e:
            print(f"Reranking failed: {e}")
            return [(doc, 0.5) for doc in documents[:top_k]]


def simple_rerank(
    query: str,
    documents: List[Document],
    top_k: int = 5
) -> List[Tuple[Document, float]]:
    """
    Simple reranking based on keyword overlap and document length.
    Used as fallback when cross-encoder is unavailable.
    """
    query_tokens = set(query.lower().split())
    
    scored_docs = []
    for doc in documents:
        content_tokens = set(doc.page_content.lower().split()[:100])  # First 100 tokens
        
        # Calculate overlap
        overlap = len(query_tokens & content_tokens) / (len(query_tokens) + 1)
        
        # Bonus for chunk with good metadata
        source_score = 1.0 if doc.metadata.get('source') else 0.5
        
        # Combined score
        score = overlap * source_score
        scored_docs.append((doc, score))
    
    # Sort and return top-k
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return scored_docs[:top_k]
