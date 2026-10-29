"""Ingest local data/ into two Qdrant Cloud collections.

HR .txt files go into the clean collection. HR + data/noise/ go into the
mixed collection used for retrieval reliability tests.
"""

from __future__ import annotations

import argparse
import logging

from hr_assistant import config
from hr_assistant.document_loader import load_documents, load_hr_documents
from hr_assistant.splitter import split_into_chunks
from hr_assistant.vector_store import build_vector_store, collection_exists

logger = logging.getLogger(__name__)


def ingest_hr_policies(force: bool = False) -> None:
    """The clean HR-only collection the app connects to."""
    name = config.QDRANT_COLLECTION_NAME
    if collection_exists(name) and not force:
        logger.info("Collection '%s' already populated — skipping (use --force to rebuild).", name)
        return

    documents = load_hr_documents()
    if not documents:
        raise RuntimeError(f"No HR policy files found under {config.DATA_DIR}")

    chunks = split_into_chunks(documents)
    build_vector_store(chunks, hybrid=True, collection_name=name)
    logger.info(
        "Ingested %d HR document(s) -> %d chunk(s) into '%s'.",
        len(documents),
        len(chunks),
        name,
    )


def ingest_noisy_corpus(force: bool = False) -> None:
    """Mixed HR + noise collection for cross-domain retrieval tests."""
    name = config.QDRANT_NOISY_COLLECTION_NAME
    if collection_exists(name) and not force:
        logger.info("Collection '%s' already populated — skipping (use --force to rebuild).", name)
        return

    documents = load_documents()
    if not documents:
        raise RuntimeError(f"No source files found under {config.DATA_DIR}")

    chunks = split_into_chunks(documents)
    build_vector_store(chunks, hybrid=True, collection_name=name)
    logger.info(
        "Ingested %d document(s) (HR + noise) -> %d chunk(s) into '%s'.",
        len(documents),
        len(chunks),
        name,
    )


def run_ingestion(force: bool = False, hr: bool = True, noisy: bool = True) -> None:
    config.check_api_keys()
    if hr:
        ingest_hr_policies(force=force)
    if noisy:
        ingest_noisy_corpus(force=force)


def main() -> None:
    from hr_assistant.logging_config import configure_logging

    configure_logging()
    parser = argparse.ArgumentParser(description="Ingest local data/ into Qdrant Cloud.")
    parser.add_argument("--force", action="store_true", help="Rebuild even if the collection already has points.")
    parser.add_argument("--hr-only", action="store_true", help="Ingest only the clean HR collection.")
    parser.add_argument("--noisy-only", action="store_true", help="Ingest only the mixed HR + noise collection.")
    args = parser.parse_args()

    hr = not args.noisy_only
    noisy = not args.hr_only
    run_ingestion(force=args.force, hr=hr, noisy=noisy)


if __name__ == "__main__":
    main()
