import hashlib
import os
import shutil
from pathlib import Path

CHUNK_SIZE = 8192
DEFAULT_LIBRARY_ROOT = Path(os.environ.get("LIBRARY_ROOT", "library_files"))


def compute_hash(path: Path | str) -> str:
    path = Path(path)  # ensure Path object
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def store_file(src_path: str) -> dict[str, str]:
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

    return {
        "hash": file_hash,
        "stored_path": str(dest_path),
        "format": ext,
    }
