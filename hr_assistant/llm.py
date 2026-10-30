"""Chat model: Native ChatGoogleGenerativeAI (Gemini) with Groq (ChatOpenAI) as fallback."""

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from hr_assistant import config


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Native Gemini chat model with Groq fallback — pure LangChain, no LiteLLM.

    Primary: ChatGoogleGenerativeAI using the cost-effective and available
    gemini-3.5-flash-lite (or configured LLM_MODEL_NAME).
    Fallback: ChatOpenAI pointing to Groq's endpoint.
    """
    if not config.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing from the environment.")
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing from the environment.")

    model_name = config.LLM_MODEL_NAME
    if model_name.startswith("gemini/"):
        model_name = model_name.removeprefix("gemini/")

    primary = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=1.0,
    )

    fallback = ChatOpenAI(
        model=config.FALLBACK_MODEL_NAME,
        openai_api_key=config.GROQ_API_KEY,
        openai_api_base=config.GROQ_BASE_URL,
        temperature=0,
    )

    return primary.with_fallbacks([fallback])
