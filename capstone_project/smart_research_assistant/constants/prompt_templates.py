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
    return f"""Context:
        {context}

        Question: "{query}"
        
        Only use the information provided in the context and references. Do not use prior knowledge. 
        If the answer is not found in the context, say: "Not enough information available to answer your question."

        Use **Markdown** formatting.
        Structure the answer with clear sections and bullet points.

        Answer: """
