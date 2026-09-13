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

            model_name = settings.GEMINI_MODEL or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            return ChatGoogleGenerativeAI(
                model=model_name,
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
        import traceback
        import sys

        # Step 1: Attempt Primary LLM
        if self.primary_llm and self.is_key_valid(self.key1):
            try:
                chain = chain_builder(self.primary_llm)
                result = await chain.ainvoke(inputs)
                if result is not None:
                    return result
            except Exception as primary_exc:
                print(f"\n[GEMINI FAILOVER] Primary Gemini API key (KEY_1) failed: {primary_exc}", file=sys.stderr, flush=True)
                traceback.print_exc()
                logger.warning(
                    f"[GEMINI FAILOVER] Primary Gemini key failed ({primary_exc}). "
                    "Initiating transparent failover to secondary GEMINI_API_KEY_2..."
                )

        # Step 2: Attempt Secondary LLM
        if self.secondary_llm and self.is_key_valid(self.key2):
            try:
                chain = chain_builder(self.secondary_llm)
                result = await chain.ainvoke(inputs)
                if result is not None:
                    print("[GEMINI SUCCESS] Secondary Gemini API key execution succeeded cleanly after primary failover.", flush=True)
                    logger.info("Secondary Gemini API key execution succeeded cleanly after primary failover.")
                    return result
            except Exception as secondary_exc:
                print(f"\n[GEMINI FAILOVER ERROR] Secondary Gemini API key (KEY_2) also failed: {secondary_exc}", file=sys.stderr, flush=True)
                traceback.print_exc()
                logger.error(
                    f"Secondary Gemini API key also failed ({secondary_exc}). "
                    "Falling back to score-grounded deterministic engine output."
                )
        else:
            if self.primary_llm and self.is_key_valid(self.key1):
                print("[GEMINI NOTICE] Secondary GEMINI_API_KEY_2 not configured or invalid for failover retry.", flush=True)
                logger.warning("Secondary GEMINI_API_KEY_2 not configured for failover retry.")

        # Step 3: Score-grounded deterministic fallback
        print("[GEMINI FALLBACK] Invoking score-grounded fallback handler to guarantee zero 500 internal server errors.", flush=True)
        logger.info("Invoking score-grounded fallback handler to guarantee zero 500 internal server errors.")
        return fallback_fn(inputs)

# Shared singleton manager
gemini_manager = GeminiClientManager()
