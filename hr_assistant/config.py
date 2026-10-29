import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Local policy corpus. Point DATA_DIR elsewhere (or swap the loader) when a
# remote store is chosen later — nothing here talks to Google Cloud.
DATA_DIR = Path(os.getenv("DATA_DIR", str(_PROJECT_ROOT / "data")))

# Parsed JSON records written by processor.py (HR vs noise subfolders).
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", str(DATA_DIR / "processed")))
PROCESSED_HR_DIR = PROCESSED_DIR / "hr"
PROCESSED_NOISE_DIR = PROCESSED_DIR / "noise"

## ENV VAR / SECRETS

JINA_API_KEY = os.getenv("JINA_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

## QDRANT

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "hybrid-rag")

# Reliability path: a separate collection holding HR docs + non-HR noise
# together, so retrieval is tested against real cross-domain noise instead
# of the clean single-domain collection above.
QDRANT_NOISY_COLLECTION_NAME = os.getenv("QDRANT_NOISY_COLLECTION_NAME", "hr_policies_noisy_demo")

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")

FALLBACK_MODEL_NAME = os.getenv("FALLBACK_MODEL_NAME", "openai/gpt-oss-20b")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "jina-embeddings-v2-base-en")

RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "jina-reranker-v2-base-multilingual")

## CHUNK / TEXT SPLITTING CONFIG

CHUNK_SIZE = 500
CHUNK_OVERLAP = 60

## RETRIEVAL RESULTS
TOP_K_RESULTS = 5
RERANK_CANDIDATE_K = 12  # wider shortlist retrieved before re-ranking

## RELIABILITY — scope guardrail (see hr_assistant/tools.py)

# Exact values used in each policy file's "Policy Category:" line. The
# search tool hard-filters retrieval to only these categories — non-HR
# chunks (Finance/Sales/Operations/Business) are structurally unreachable,
# regardless of how confused embedding similarity gets.
HR_POLICY_CATEGORIES = {
    "Leave", "Work From Home", "Probation", "Notice Period", "Reimbursement",
    "Code of Conduct", "Holidays", "Maternity Paternity", "Travel Expense", "Exit Process",
}

# Post-rerank relevance score cutoff — below this, the tool reports "not
# found" instead of returning a stray, technically-in-scope-but-irrelevant
# chunk. Jina relevance scores are ~0-1; this is a starting point, calibrate
# empirically against real queries rather than trusting it blindly.
RELEVANCE_THRESHOLD = 0.35



## RELIABILITY — semantic cache

SEMANTIC_CACHE_THRESHOLD = 0.93  # cosine similarity above this = cache hit

# Bound the in-memory cache: a long-lived process shouldn't grow forever,
# and a stale answer (policy changed + re-ingested) shouldn't be served
# indefinitely. Past MAX_ENTRIES the oldest entry is evicted; entries older
# than TTL_SECONDS are ignored on lookup (0 = never expire).
SEMANTIC_CACHE_MAX_ENTRIES = int(os.getenv("SEMANTIC_CACHE_MAX_ENTRIES", "500"))
SEMANTIC_CACHE_TTL_SECONDS = int(os.getenv("SEMANTIC_CACHE_TTL_SECONDS", "3600"))

## LANGSMITH — tracing (the app) + datasets/experiments (evaluate.py)
# Env-var based: langchain/langgraph auto-trace when these are set. The
# @traceable-decorated guardrail/cache functions pick them up the same way.

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "hybrid-rag")

## JUDGE LLM — Groq, read by hr_assistant/evaluation.py.
# A different model family from the app's Gemini, so the eval isn't the
# model grading its own answers. gpt-oss on Groq is OpenAI-API-compatible,
# so langchain-openai's ChatOpenAI talks to it directly — no new dependency.
# GROQ_API_KEY is also the credential for the app's fallback model
# (FALLBACK_MODEL_NAME, above — see hr_assistant/llm.py).

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
JUDGE_MODEL_NAME = os.getenv("JUDGE_MODEL_NAME", "openai/gpt-oss-120b")


def check_api_keys() -> None:
    missing = [
        name
        for name, value in (
            ("JINA_API_KEY", JINA_API_KEY),
            ("QDRANT_URL", QDRANT_URL),
            ("QDRANT_API_KEY", QDRANT_API_KEY),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")




