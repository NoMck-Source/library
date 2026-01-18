import json
import os
from pathlib import Path

DEFAULT_LIBRARY_ROOT = Path(os.environ.get("LIBRARY_ROOT", "library_files"))
INDEX_FILE = DEFAULT_LIBRARY_ROOT / "library_index.json"


def load_index() -> list[dict]:
    # Load the library index from the JSON file or return an empty list if it doesn't exist
    if INDEX_FILE.exists():
        with INDEX_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_index(entries: list[dict]) -> None:
    # Save the library index to the JSON file
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
