"""Primary LiteLLM gateway model with a Groq fallback."""

import logging
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from hr_assistant import config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Create the shared model, using LiteLLM when configured.

    Groq is kept as an independent fallback and can also serve as the primary
    when the optional LiteLLM gateway is not configured.
    """
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing from the environment.")

    fallback = ChatOpenAI(
        model=config.FALLBACK_MODEL_NAME,
        api_key=config.GROQ_API_KEY,
        base_url=config.GROQ_BASE_URL,
        temperature=0,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_retries=config.LLM_MAX_RETRIES,
    )

    if not config.LITELLM_API_KEY:
        logger.warning("LITELLM_API_KEY is not configured; using Groq as the primary LLM.")
        return fallback

    primary = ChatOpenAI(
        model=config.LLM_MODEL_NAME,
        api_key=config.LITELLM_API_KEY,
        base_url=config.LITELLM_BASE_URL,
        temperature=0,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_retries=config.LLM_MAX_RETRIES,
    )
    return primary.with_fallbacks([fallback])
