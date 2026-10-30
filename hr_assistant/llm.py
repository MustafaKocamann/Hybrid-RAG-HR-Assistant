"""Chat model: Google AI Studio Gemini via LiteLLM Router, Groq as fallback."""

from functools import lru_cache

from langchain_litellm import ChatLiteLLMRouter
from litellm import Router

from hr_assistant import config

PRIMARY_DEPLOYMENT = "primary"
FALLBACK_DEPLOYMENT = "fallback"


def _gemini_model_id() -> str:
    """LiteLLM AI Studio id: gemini/<model>. Strip a leftover Vertex prefix."""
    name = config.LLM_MODEL_NAME
    if name.startswith("vertex_ai/"):
        name = name.removeprefix("vertex_ai/")
    if name.startswith("gemini/"):
        return name
    return f"gemini/{name}"


def _fallback_model_params() -> dict:
    """Format model and params for the Groq fallback. LiteLLM routes Groq models
    using 'groq/<model>' or 'openai/<model>' when api_base is configured."""
    model = config.FALLBACK_MODEL_NAME
    if model.startswith("openai/"):
        model = f"openai/{model}"
    elif not model.startswith("groq/"):
        model = f"groq/{model}"
    return {
        "model": model,
        "api_key": config.GROQ_API_KEY,
        "api_base": config.GROQ_BASE_URL,
    }


@lru_cache(maxsize=1)
def _get_router() -> Router:
    if not config.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing from the environment.")
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing from the environment.")

    return Router(
        model_list=[
            {
                "model_name": PRIMARY_DEPLOYMENT,
                "litellm_params": {
                    "model": _gemini_model_id(),
                    "api_key": config.GOOGLE_API_KEY,
                },
            },
            {
                "model_name": FALLBACK_DEPLOYMENT,
                "litellm_params": _fallback_model_params(),
            },
        ],
        fallbacks=[{PRIMARY_DEPLOYMENT: [FALLBACK_DEPLOYMENT]}],
        num_retries=2,
        retry_after=5,
        allowed_fails=1,
        cooldown_time=30,
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatLiteLLMRouter:
    """Singleton ChatLiteLLMRouter: Gemini primary, Groq fallback.

    bind_tools() and with_structured_output() work on the returned model
    because ChatLiteLLMRouter is a standard LangChain chat model.
    """
    return ChatLiteLLMRouter(
        router=_get_router(),
        model_name=PRIMARY_DEPLOYMENT,
        temperature=0,
    )
