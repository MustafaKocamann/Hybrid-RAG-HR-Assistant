"""Chat model configured through the OpenAI-compatible LiteLLM gateway."""

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from hr_assistant import config


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Create the shared gateway client.

    Provider routing and provider-level fallbacks belong to LiteLLM. Keeping a
    single client here avoids an extra provider hop and makes latency settings
    consistent for every agent invocation.
    """
    if not config.LITELLM_API_KEY:
        raise RuntimeError("LITELLM_API_KEY is missing from the environment.")

    return ChatOpenAI(
        model=config.LLM_MODEL_NAME,
        api_key=config.LITELLM_API_KEY,
        base_url=config.LITELLM_BASE_URL,
        temperature=0,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_retries=config.LLM_MAX_RETRIES,
    )
