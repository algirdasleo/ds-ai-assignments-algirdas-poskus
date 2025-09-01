from typing import List


def query_improvement_prompt(query: str) -> str:
    return f"""
        Improve the following user query so it works well for:
        1. AI-powered document retrieval (RAG)
        2. Keyword-based web search.

        Make the query clear, include relevant technical terms, and avoid ambiguity.
        
        Original Query: {query}
        
        Improved Query (with no explanations):
    """


def context_rating_prompt(query: str, rag_context: List, web_search_context: List) -> str:
    return f"""
        Query: {query}
        RAG Context: {rag_context}
        Web Search Context: {web_search_context}

        Rate the current context and answer - should web search be used to:
        - Improve the depth of the answer
        - Answer the question at all (if RAG found no relevant documents)?
        Be strict and always lean towards getting more information
    """


def ai_ml_topic_check_prompt(query: str):
    return f"""
        Is the topic of the following query AI/ML related?
        Query: {query}
    """


def generate_answer_prompt(context: str, query: str) -> str:
    return f"""
        Context: "{context}"
        Question: "{query}"
        
        
        Rules:
        1. Do not use **any** prior knowledge. 
        2. You **must** include a reference for every fact or idea derived from the context or web search results, even if paraphrased.
        3. Use Markdown formatting. Structure the answer with clear sections and bullet points.
        4. If unable to answer, say: "Not enough information available to answer your question."
        
        Each reference object must have the following fields:
        - "title": string or null
        - "quote": string (required)
        - "url": string (required)
        - "chunk_idx": integer or null
        """
