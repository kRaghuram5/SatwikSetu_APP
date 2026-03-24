"""
RAG Chain — core advisory generation pipeline.
LLM-only advisory generation (no mock fallback).
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from app.rag.vectorstore import get_vectorstore
from app.rag.prompts import (
    ADVISORY_SYSTEM_PROMPT,
    ADVISORY_USER_PROMPT,
)
from app.config import get_advisory_settings

# Try to import LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available")


class AdvisoryChain:
    """RAG chain for generating treatment advisories."""

    def __init__(self):
        self.settings = get_advisory_settings()
        self.vectorstore = get_vectorstore()
        self.llm = None

        if self.settings.LLM_PROVIDER != "openai":
            raise RuntimeError("Only LLM_PROVIDER=openai is supported.")

        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("langchain-openai is not installed in ai-advisory service.")

        if not self.settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is missing; LLM advisory is required.")

        try:
            kwargs = dict(
                model=self.settings.OPENAI_MODEL,
                temperature=0.3,
                api_key=self.settings.OPENAI_API_KEY,
            )
            if self.settings.OPENAI_BASE_URL:
                kwargs["base_url"] = self.settings.OPENAI_BASE_URL
            self.llm = ChatOpenAI(**kwargs)
            logger.info("OpenAI LLM initialized")
        except Exception as e:
            raise RuntimeError(f"Could not initialize OpenAI client: {e}") from e

    async def generate_advisory(
        self,
        disease: str,
        crop: str,
        confidence: float,
        location: Optional[str] = None,
    ) -> dict:
        """
        Generate treatment advisory using RAG.

        1. Search vector store for relevant documents
        2. Construct prompt with context
        3. Call LLM for advisory
        """
        # Step 1: Vector search
        query = f"{crop} {disease} treatment advice"
        context_docs = self.vectorstore.search(query, crop=crop, n_results=3)
        context = "\n\n---\n\n".join(context_docs) if context_docs else "No specific knowledge base entries found."

        # Step 2 & 3: LLM-only generation
        return await self._llm_generate(disease, crop, confidence, location, context)

    async def _llm_generate(
        self, disease: str, crop: str, confidence: float,
        location: Optional[str], context: str,
    ) -> dict:
        """Generate advisory using actual LLM."""
        user_prompt = ADVISORY_USER_PROMPT.format(
            crop=crop,
            disease=disease,
            confidence=round(confidence * 100, 1),
            location=location or "Not specified",
            context=context,
        )

        messages = [
            SystemMessage(content=ADVISORY_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            # Try to parse as JSON
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"LLM response parsing error: {e}")
            raise RuntimeError("Failed to generate advisory from LLM response.") from e


# Singleton
_chain = None


def get_advisory_chain() -> AdvisoryChain:
    """Get or create singleton advisory chain."""
    global _chain
    if _chain is None:
        _chain = AdvisoryChain()
    return _chain
