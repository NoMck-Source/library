import hashlib
import json
import os
import shutil
from pathlib import Path

from .metadata import extract_epub_metadata
from .utils import load_index, save_index

CHUNK_SIZE = 8192
DEFAULT_LIBRARY_ROOT = Path(os.environ.get("LIBRARY_ROOT", "library_files"))
INDEX_FILE = DEFAULT_LIBRARY_ROOT / "library_index.json"


def compute_hash(path: Path | str) -> str:
    path = Path(path)  # ensure Path object
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def store_file(src_path: str | Path) -> dict[str, object]:
    # Store a file in the library and return its hash as filename.
    src = Path(src_path)
    file_hash = compute_hash(src)

    ext = src.suffix.lower().lstrip(".")
    if not ext:
        raise ValueError("File has no extension")

    dest_dir = DEFAULT_LIBRARY_ROOT / ext
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / f"{file_hash}.{ext}"

    if not dest_path.exists():
        shutil.copy2(src, dest_path)

    metadata = {}
    if ext == "epub":
        try:
            metadata = extract_epub_metadata(dest_path)
        except Exception as e:
            # On failure return empty metadata
            metadata = {"title": None, "author": None}
    index = load_index()
    if not any(entry["hash"] == file_hash for entry in index):
        index.append(
            {
                "hash": file_hash,
                "stored_path": str(dest_path),
                "format": ext,
                "metadata": metadata,
            }
        )
    save_index(index)

    return {
        "hash": file_hash,
        "stored_path": str(dest_path),
        "format": ext,
        "metadata": metadata,
    }


def import_folder(
    folder_path: str | Path, recursive: bool = True
) -> list[dict[str, object]]:
    """
    Scans folder for EPUB files and stores them in Library
    Returns a list of info dicts for each stored file.
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    stored_files = []

    pattern = "**/*.epub" if recursive else "*.epub"
    for epub_file in folder_path.glob(pattern):
        if epub_file.is_file():
            try:
                info = store_file(epub_file)
                stored_files.append(info)
            except Exception as e:
                print(f"Failed to store {epub_file}: {e}")
    return stored_files
