from hr_assistant.logging_config import configure_logging
from hr_assistant.pipeline import build_reliability_assistant

configure_logging()

# Studio drives the raw agent graph — the semantic cache and the
# input/output safety guardrails live in pipeline.ask(), not the agent, so
# they are not exercised here. That's intentional: Studio is for inspecting
# the agent's own nodes/edges/state.
agent, _cache = build_reliability_assistant(use_checkpointer=False)

# langgraph.json points at this module-level name
graph = agent