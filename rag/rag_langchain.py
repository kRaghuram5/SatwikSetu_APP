"""
RAG Pipeline with LangChain + Qdrant

Flow:
    1. Load documents into a vector store (Qdrant)
    2. User asks a question
    3. Vector search retrieves relevant documents
    4. LLM generates an answer using those documents as context

Run:

    uvicorn concepts_copy.rag_api:app --reload --port 9006

Test:
    http://localhost:9006/docs
"""

