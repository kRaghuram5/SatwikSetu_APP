"""Advisory retrieval and knowledge base search endpoints."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models.advisory import Advisory
from shared.models.upload import Upload
from app.rag.vectorstore import get_vectorstore

router = APIRouter()


@router.get("/advisory/search")
def search_knowledge_base(
    query: str = Query(..., description="Search query e.g. 'tomato late blight treatment'"),
    crop: str = Query(None, description="Filter by crop (e.g. Tomato, Potato)"),
    top_k: int = Query(3, ge=1, le=10, description="Number of results to return"),
):
    """
    Search the Qdrant vector store for disease knowledge.

    Useful for:
    - Exploring what the knowledge base contains
    - Getting raw context before advisory generation
    - Debugging RAG retrieval quality
    """
    vectorstore = get_vectorstore()
    results = vectorstore.search(query=query, crop=crop, n_results=top_k)

    if not results:
        return {
            "query": query,
            "crop_filter": crop,
            "results": [],
            "message": "No matching documents found. Qdrant may be unavailable or knowledge base not loaded.",
        }

    return {
        "query": query,
        "crop_filter": crop,
        "total": len(results),
        "results": [{"rank": i + 1, "content": doc} for i, doc in enumerate(results)],
    }


@router.get("/advisory/{upload_id}")
def get_advisory(
    upload_id: str,
    farmer_id: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    Retrieve AI-generated advisory for a specific upload.
    The advisory is generated asynchronously via Kafka after disease detection.
    """
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    advisory = db.query(Advisory).filter(Advisory.upload_id == upload_id).first()
    if not advisory:
        return {
            "upload_id": upload_id,
            "status": "processing",
            "message": "Advisory is being generated. Please try again in a few seconds.",
        }

    prevention = advisory.prevention
    try:
        prevention = json.loads(prevention) if isinstance(prevention, str) else prevention
    except json.JSONDecodeError:
        prevention = [prevention] if prevention else []

    return {
        "upload_id": upload_id,
        "advisory_id": str(advisory.id),
        "disease": upload.disease_detected,
        "crop": upload.crop,
        "confidence": upload.confidence,
        "treatment": advisory.treatment,
        "organic_alternative": advisory.organic_alternative,
        "prevention": prevention,
        "fertilizer_recommendation": advisory.fertilizer,
        "created_at": advisory.created_at.isoformat() if advisory.created_at else None,
    }
