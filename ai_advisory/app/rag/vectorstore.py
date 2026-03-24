"""Qdrant vector store management for the farming knowledge base."""

import json
import logging
import os
import uuid
from typing import List

logger = logging.getLogger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue,
    )
    from sentence_transformers import SentenceTransformer
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant or SentenceTransformers not available")


class FarmingVectorStore:
    """Manages the Qdrant collection for farming knowledge."""

    COLLECTION_NAME = "farming_knowledge"

    def __init__(self, host: str = "qdrant", port: int = 6333):
        self.client = None
        self.encoder = None

        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(host=host, port=port)
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
                
                # Check/Create collection (compatible with qdrant-client 1.7.x)
                try:
                    self.client.get_collection(self.COLLECTION_NAME)
                except Exception:
                    self.client.create_collection(
                        collection_name=self.COLLECTION_NAME,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                    )
                logger.info(f"Connected to Qdrant at {host}:{port}")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant: {e}")

    def load_knowledge_base(self, knowledge_dir: str):
        """Load JSON files from the knowledge base directory into Qdrant."""
        if not self.client or not self.encoder:
            logger.warning("No Qdrant client — skipping knowledge load")
            return

        diseases_path = os.path.join(knowledge_dir, "diseases.json")
        if not os.path.exists(diseases_path):
            logger.warning(f"Knowledge file not found: {diseases_path}")
            return

        with open(diseases_path, "r") as f:
            diseases = json.load(f)

        documents = []
        metadatas = []
        
        for disease in diseases:
            # Create a rich text document for embedding
            doc_text = (
                f"Crop: {disease['crop']}\n"
                f"Disease: {disease['disease']}\n"
                f"Description: {disease['description']}\n"
                f"Treatment: {disease['treatment']}\n"
                f"Organic Alternative: {disease['organic_alternative']}\n"
                f"Prevention: {', '.join(disease['prevention'])}\n"
                f"Fertilizer: {disease['fertilizer']}"
            )
            documents.append(doc_text)
            metadatas.append({
                "crop": disease["crop"],
                "disease": disease["disease"],
            })

        # Generate embeddings
        embeddings = self.encoder.encode(documents)
        
        points = []
        for i, (doc, meta, embedding) in enumerate(zip(documents, metadatas, embeddings)):
            # Generate deterministic UUID based on content to avoid duplicates
            doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc))
            points.append(PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload={"content": doc, "metadata": meta}
            ))

        try:
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            logger.info(f"Loaded {len(documents)} disease documents into Qdrant")
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")

    def search(self, query: str, crop: str = None, n_results: int = 3) -> List[str]:
        """Search the vector store for relevant documents."""
        if not self.client or not self.encoder:
            return []

        try:
            query_vector = self.encoder.encode(query).tolist()

            query_filter = None
            if crop:
                query_filter = Filter(
                    must=[FieldCondition(key="metadata.crop", match=MatchValue(value=crop))]
                )

            points = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=n_results,
            )
            return [hit.payload["content"] for hit in points]

        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []


# Singleton
_vectorstore = None


def get_vectorstore() -> FarmingVectorStore:
    """Get or create singleton vector store instance."""
    global _vectorstore
    if _vectorstore is None:
        from app.config import get_advisory_settings
        settings = get_advisory_settings()
        _vectorstore = FarmingVectorStore(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        _vectorstore.load_knowledge_base(settings.KNOWLEDGE_BASE_DIR)
    return _vectorstore
