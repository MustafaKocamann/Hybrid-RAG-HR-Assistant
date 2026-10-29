import logging
import os

_CONFIGURED = False


def configure_logging(level: "str | int | None" = None) -> None:
    """Attach a plain-message handler to the root logger, once per process.

    Level: the explicit arg, else $LOG_LEVEL, else INFO. Idempotent —
    safe to call from every entry point and from a Streamlit rerun.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(
        level=level or os.getenv("LOG_LEVEL", "INFO"),
        format="%(message)s",
    )
    # Streamlit configures the root logger before our code runs, so
    # basicConfig above is a no-op there; make sure our package's lines
    # still pass the level filter.
    logging.getLogger("hybrid-rag").setLevel(level or os.getenv("LOG_LEVEL", "INFO"))
    _CONFIGURED = True