import os
import logging
from typing import Any, Callable, Dict, Optional, TypeVar
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

logger = logging.getLogger("bizmatch.ai_client")

T = TypeVar("T")

class GeminiClientManager:
    """
    Resilient dual-key provider for Google Gemini.
    Manages primary and secondary API keys, transparently failing over to GEMINI_API_KEY_2
    if GEMINI_API_KEY_1 encounters rate limits (429), quota exhaustion, or timeouts.
    If both fail, executes score-grounded deterministic fallback.
    """

    def __init__(self):
        self.key1 = settings.GEMINI_API_KEY_1 or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY_1") or os.environ.get("GEMINI_API_KEY", "")
        self.key2 = settings.GEMINI_API_KEY_2 or os.environ.get("GEMINI_API_KEY_2", "")

        self.primary_llm: Optional[ChatGoogleGenerativeAI] = self._create_llm_instance(self.key1, "Primary (KEY_1)")
        self.secondary_llm: Optional[ChatGoogleGenerativeAI] = self._create_llm_instance(self.key2, "Secondary (KEY_2)")

    def _create_llm_instance(self, api_key: str, label: str) -> Optional[ChatGoogleGenerativeAI]:
        if not self.is_key_valid(api_key):
            logger.info(f"Gemini API key for {label} is unconfigured or in test mode.")
            return None
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                google_api_key=api_key
            )
        except Exception as exc:
            logger.warning(f"Failed to initialize ChatGoogleGenerativeAI for {label}: {exc}")
            return None

    def is_key_valid(self, api_key: str) -> bool:
        if not api_key:
            return False
        invalid_patterns = ("test_key", "dummy_key", "your_", "placeholder", "xxx")
        return not any(pat in api_key.lower() for pat in invalid_patterns)

    async def execute_with_failover(
        self,
        chain_builder: Callable[[ChatGoogleGenerativeAI], Any],
        inputs: Dict[str, Any],
        fallback_fn: Callable[[Dict[str, Any]], T]
    ) -> T:
        """
        Executes a LangChain/LLM operation with automatic key failover:
        1. Tries primary key (GEMINI_API_KEY_1).
        2. On 429 / rate limit / quota exhaustion / error, transparently retries with GEMINI_API_KEY_2.
        3. On double failure, returns score-grounded fallback.
        """
        # Step 1: Attempt Primary LLM
        if self.primary_llm and self.is_key_valid(self.key1):
            try:
                chain = chain_builder(self.primary_llm)
                result = await chain.ainvoke(inputs)
                if result is not None:
                    return result
            except Exception as primary_exc:
                logger.warning(
                    f"Primary Gemini API key failed (Error: {primary_exc}). "
                    "Initiating transparent failover to secondary GEMINI_API_KEY_2..."
                )

        # Step 2: Attempt Secondary LLM
        if self.secondary_llm and self.is_key_valid(self.key2):
            try:
                chain = chain_builder(self.secondary_llm)
                result = await chain.ainvoke(inputs)
                if result is not None:
                    logger.info("Secondary Gemini API key execution succeeded cleanly after primary failover.")
                    return result
            except Exception as secondary_exc:
                logger.error(
                    f"Secondary Gemini API key also failed (Error: {secondary_exc}). "
                    "Falling back to score-grounded deterministic engine output."
                )
        else:
            if self.primary_llm and self.is_key_valid(self.key1):
                logger.warning("Secondary GEMINI_API_KEY_2 not configured for failover retry.")

        # Step 3: Score-grounded deterministic fallback
        logger.info("Invoking score-grounded fallback handler to guarantee zero 500 internal server errors.")
        return fallback_fn(inputs)

# Shared singleton manager
gemini_manager = GeminiClientManager()
