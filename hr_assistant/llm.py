"""Primary LiteLLM gateway model with a Groq fallback."""

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from hr_assistant import config


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Create the shared primary model and provider fallback.

    The primary model is routed through LiteLLM. Groq is kept as an independent
    fallback so the application can recover when the gateway is unavailable.
    """
    if not config.LITELLM_API_KEY:
        raise RuntimeError("LITELLM_API_KEY is missing from the environment.")
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing from the environment.")

    primary = ChatOpenAI(
        model=config.LLM_MODEL_NAME,
        api_key=config.LITELLM_API_KEY,
        base_url=config.LITELLM_BASE_URL,
        temperature=0,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_retries=config.LLM_MAX_RETRIES,
    )
    fallback = ChatOpenAI(
        model=config.FALLBACK_MODEL_NAME,
        api_key=config.GROQ_API_KEY,
        base_url=config.GROQ_BASE_URL,
        temperature=0,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_retries=config.LLM_MAX_RETRIES,
    )

    return primary.with_fallbacks([fallback])
