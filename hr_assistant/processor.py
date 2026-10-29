"""Turn raw files from data/ into processed JSON records on disk.

Uses document_loader for parsing. Replace the output paths later if a remote
store is chosen — the record shape stays the same.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from hr_assistant import config
from hr_assistant.document_loader import load_documents

logger = logging.getLogger(__name__)


def process_raw_to_json(
    data_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> int:
    """Parse every local source file and write one JSON record per file.

    Returns how many records were written. Each record holds what
    `load_processed_documents` reads back: source, policy_category, text,
    source_path.
    """
    docs = load_documents(data_dir)
    out_root = Path(processed_dir) if processed_dir is not None else config.PROCESSED_DIR
    hr_dir = out_root / "hr"
    noise_dir = out_root / "noise"
    hr_dir.mkdir(parents=True, exist_ok=True)
    noise_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in docs:
        meta = doc.metadata
        source = meta["source"]
        dest_dir = noise_dir if source.startswith("noise/") else hr_dir
        record = {
            "source": meta["filename"],
            "policy_category": meta["category"],
            "text": doc.page_content,
            "source_path": source,
        }

        processed_name = Path(meta["filename"]).stem + ".json"
        dest = dest_dir / processed_name
        dest.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("  %s  ->  %s", source, dest.relative_to(out_root).as_posix())
        count += 1

    return count


def load_processed_documents(processed_dir: Path | None = None) -> list[dict]:
    """Read processed JSON records written by `process_raw_to_json`."""
    root = Path(processed_dir) if processed_dir is not None else config.PROCESSED_DIR
    if not root.is_dir():
        raise FileNotFoundError(f"Processed directory not found: {root}")

    records: list[dict] = []
    for path in sorted(root.rglob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    written = process_raw_to_json()
    print(f"Wrote {written} records to {config.PROCESSED_DIR}")
