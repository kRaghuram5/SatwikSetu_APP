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
import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / '.env')
KNOWLEDGE_FILE = Path(__file__).parent / 'farming_knowledge_06_v2.json'
PROMPTS_FILE = Path(__file__).parent / 'prompts_06.json'

from sentence_transformers import SentenceTransformer
from qdrant_ingestion import QdrantIngestion

class SimpleVectorStore:
    def __init__(self, knowledge_path: Path | None = None):
        self.collection_name = "farming_knowledge"
        self.ingestion = QdrantIngestion(collection_name=self.collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        if knowledge_path:
            self.ingestion.load_and_ingest(knowledge_path, self.encoder)

    def search(self, query: str, n_results: int = 3):
        query_vector = self.encoder.encode(query).tolist()
        results = self.ingestion.client.query_points(
            collection_name = self.collection_name,
            query = query_vector,
            limit = n_results,
        )
        return [
            {
                "content": hit.payload["content"],
                "metadata": hit.payload["metadata"],
                "distance": hit.score,
            }
            for hit in results.points
        ]

class LLMProvider:
    def __init__(self,prompts: dict):
        self.prompts = prompts
        self.llm = None  # Placeholder for actual LLM client (e.g., OpenAI, HuggingFace)

        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"), temperature=0.7)
        except Exception as e:
            raise RuntimeError(
                "OpenAI LLM initialization failed."
                "Configure openai credentials and model in the .env file. Error: " + str(e)
            ) from e
    
    def generate_answer(self, question: str, context: str) -> str:
        
        from langchain_core.messages import SystemMessage, HumanMessage

        messages = [
            SystemMessage(content=self.prompts["system_prompt"]),
            HumanMessage(content=self.prompts["human_prompt_template"].format(question=question, context=context))
        ]
        response = self.llm.invoke(messages)
        return response.content
    
class RAGPipeline:
    def __init__(
            self,
            knowledge_path: Path = KNOWLEDGE_FILE,
            prompts_path: Path = PROMPTS_FILE
    ):
        self.prompts = self.load_json(prompts_path)
        self.vector_store = SimpleVectorStore(knowledge_path=knowledge_path)
        self.llm_provider = LLMProvider(prompts=self.prompts)

    def load_json(self, path: Path) -> dict | list:
        with path.open('r',encoding = 'utf-8') as f:
            return json.load(f)
    
    def query(self, question: str, n_results: int = 3) -> str:
        results = self.vector_store.search(question, n_results=n_results)
        context_parts = []
        sources = []
        # step 2: Build context from retrieved documents
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Source {i}]: {result['content']}")
            sources.append(
                {
                    "source_id": i,
                    "crop": result['metadata'].get('crop'),
                    "topic": result['metadata'].get('topic'),
                    "relevance_score": round(result.get('distance', 0), 4),
                }
            )
        context = "\n\n".join(context_parts)
        # step 3: Generate answer using LLM

        answer = self.llm_provider.generate_answer(question, context)
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "num_sources_used": len(sources),
        }


