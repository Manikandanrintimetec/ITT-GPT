from typing import List
from app.llm.factory import LLMFactory


class QueryRewriter:
    """Rewrites and expands queries for better retrieval."""
    
    @staticmethod
    def rewrite_query(original_query: str, provider: str = "openrouter") -> List[str]:
        """
        Rewrites the original query and generates related queries.
        Returns list of queries to search for.
        """
        try:
            llm = LLMFactory.get_llm(provider)
            
            prompt = f"""Given the user query, generate 3-5 different ways to phrase or expand this query for better document retrieval.
            
Original query: {original_query}

Generate alternative phrasings that:
1. Use synonyms and related terms
2. Break down complex queries into simpler parts
3. Ask from different angles
4. Include more specific terminology

Return ONLY the alternative queries, one per line. Do not include explanations.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = llm.generate(messages)
            content = response.get("content", "")
            
            # Parse response into individual queries
            queries = [q.strip() for q in content.split("\n") if q.strip()]
            
            # Always include original query
            return [original_query] + queries[:4]
        
        except Exception:
            # Fallback to just returning the original query
            return [original_query]
    
    @staticmethod
    def decompose_query(query: str) -> List[str]:
        """Breaks down complex query into simpler sub-queries."""
        simple_rewrites = [
            query,  # Original
            f"What is {query}?",
            f"Explain {query}",
            f"Tell me about {query}"
        ]
        return simple_rewrites
