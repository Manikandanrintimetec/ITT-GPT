from typing import List, Tuple, Optional, Dict
from langchain_core.documents import Document

from app.rag.vectordb import load_vector_store
from app.rag.query_rewriter import QueryRewriter
from app.rag.bm25_retriever import BM25Retriever, hybrid_search
from app.rag.reranker import CrossEncoderReranker, simple_rerank
from app.core.logging import logger


class AdvancedRetriever:
    """
    Advanced RAG retriever with focused strategies:
    - Metadata filtering
    - Query rewriting and multihop retrieval
    - Hybrid BM25 + vector search
    - Reranking with cross-encoder
    - Semantic and recursive chunking support in document loading
    """

    def __init__(self, conversation_id: int, use_reranker: bool = True):
        self.conversation_id = conversation_id
        self.vectordb = load_vector_store(conversation_id)
        self.bm25_retriever = None
        self.reranker = None

        if self.vectordb:
            try:
                all_docs = self.vectordb.get()
                if all_docs and all_docs.get('documents'):
                    documents = [
                        Document(
                            page_content=doc,
                            metadata=meta if meta else {}
                        )
                        for doc, meta in zip(all_docs['documents'], all_docs.get('metadatas', []))
                    ]
                    self.bm25_retriever = BM25Retriever(documents)
            except Exception as e:
                logger.warning(f"Failed to initialize BM25 retriever: {e}")

        if use_reranker:
            try:
                self.reranker = CrossEncoderReranker()
            except Exception as e:
                logger.warning(f"Failed to initialize cross-encoder: {e}")

    def retrieve(
        self,
        query: str,
        k: int = 5,
        metadata_filter: Optional[Dict] = None,
        use_multi_query: bool = True,
        use_multihop: bool = True,
        use_recursive: bool = False,
        use_reranking: bool = True,
        provider: str = "openrouter"
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve documents using the selected RAG strategies.
        """
        if not self.vectordb:
            logger.warning("Vector DB not available")
            return []

        queries = [query]

        if use_multi_query:
            rewritten = QueryRewriter.rewrite_query(query, provider)
            queries = list(dict.fromkeys([query] + rewritten))
            logger.info(f"Query rewriting enabled: {len(queries)} queries")

        if use_multihop or use_recursive:
            decomposed = QueryRewriter.decompose_query(query)
            for q in decomposed:
                if q not in queries:
                    queries.append(q)
            logger.info(f"Multihop/recursive retrieval added {len(decomposed)} follow-up queries")

        all_results = self._collect_results(queries, k * 2, metadata_filter)
        all_results = self._deduplicate_docs(all_results)

        if self.bm25_retriever:
            bm25_results = []
            for q in queries:
                bm25_results.extend(self.bm25_retriever.search(q, k * 2))
            bm25_results = self._deduplicate_docs(bm25_results)
            merged = hybrid_search(all_results, bm25_results, alpha=0.6, k=k * 2)
            logger.info(f"Hybrid retrieval merged {len(merged)} candidates")
        else:
            merged = sorted(all_results, key=lambda item: item[1], reverse=True)[:k * 2]

        if use_reranking and merged:
            docs_only = [doc for doc, _ in merged]
            if self.reranker and self.reranker.model:
                merged = self.reranker.rerank(query, docs_only, top_k=k)
                logger.info("Reranked using cross-encoder")
            else:
                merged = simple_rerank(query, docs_only, top_k=k)
                logger.info("Reranked using simple fallback")
        else:
            merged = merged[:k]

        return merged[:k]

    def _collect_results(
        self,
        queries: List[str],
        k: int,
        metadata_filter: Optional[Dict]
    ) -> List[Tuple[Document, float]]:
        results = []
        for q in queries:
            try:
                vector_results = self.vectordb.similarity_search_with_score(q, k=k)
                docs = [
                    (Document(page_content=doc.page_content, metadata=doc.metadata), float(score))
                    for doc, score in vector_results
                ]
                if metadata_filter:
                    docs = self._filter_by_metadata(docs, metadata_filter)
                results.extend(docs)
            except Exception as e:
                logger.warning(f"Vector retrieval failed for '{q}': {e}")
        return results

    @staticmethod
    def _filter_by_metadata(
        docs: List[Tuple[Document, float]],
        metadata_filter: Dict
    ) -> List[Tuple[Document, float]]:
        filtered = []
        for doc, score in docs:
            match = True
            for key, value in metadata_filter.items():
                if doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append((doc, score))
        return filtered

    @staticmethod
    def _deduplicate_docs(
        docs: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        seen = set()
        unique = []
        for doc, score in docs:
            key = (doc.metadata.get('source'), doc.metadata.get('chunk_id'), hash(doc.page_content[:120]))
            if key not in seen:
                seen.add(key)
                unique.append((doc, score))
        return unique


def retrieve_advanced_context(
    conversation_id: int,
    query: str,
    k: int = 5,
    metadata_filter: Optional[Dict] = None,
    use_all_strategies: bool = True,
    provider: str = "openrouter"
) -> str:
    try:
        retriever = AdvancedRetriever(conversation_id, use_reranker=True)
        results = retriever.retrieve(
            query=query,
            k=k,
            metadata_filter=metadata_filter,
            use_multi_query=use_all_strategies,
            use_multihop=use_all_strategies,
            use_recursive=use_all_strategies,
            use_reranking=use_all_strategies,
            provider=provider
        )

        if not results:
            return ""

        context_segments = []
        for idx, (doc, score) in enumerate(results, start=1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            chunk_id = doc.metadata.get("chunk_id")
            source_label = source
            if page is not None and page != 0:
                source_label += f" | page {page + 1}"
            if chunk_id is not None:
                source_label += f" | chunk {chunk_id}"
            context_segments.append(
                f"Source {idx}: {source_label} (relevance={score:.4f})\n{doc.page_content.strip()}"
            )

        return "\n\n".join(context_segments)
    except Exception as e:
        logger.error(f"Advanced context retrieval failed: {e}")
        return ""
