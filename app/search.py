from typing import Dict, List, Optional

from .utils import load_index, save_index


def strict_search_library(index: List[Dict], query: str) -> List[Dict]:
    query = query.lower()
    return [
        book
        for book in index
        if (
            book.get("metadata", {}).get("title")
            and query in book["metadata"]["title"].lower()
        )
        or (
            book.get("metadata", {}).get("author")
            and query in book["metadata"]["author"].lower()
        )
    ]


def relaxed_search_library(haystack: str, needle: str) -> bool:
    haystack = haystack.lower()
    words = needle.lower().split()
    return all(word in haystack for word in words)


def filter_library(
    index: List[Dict],
    title: Optional[str] = None,
    author: Optional[str] = None,
    fmt: Optional[str] = None,
    mode: str = "strict",  # "strict" or "relaxed"
) -> List[Dict]:
    def cmp(haystack: str, needle: str) -> bool:
        if mode == "strict":
            return needle.lower() in haystack.lower()
        else:
            return relaxed_search_library(haystack, needle)

    # Returns books that match filters.
    results = []
    for book in index:
        md = book.get("metadata", {})

        if title and (not md.get("title") or not cmp(md["title"], title)):
            continue
        if author and (not md.get("author") or not cmp(md["author"], author)):
            continue
        if fmt and (not md.get("format") or fmt.lower() != md["format"].lower()):
            continue

        results.append(book)
    return results


def display_library(index: List[Dict]) -> None:
    for book in index:
        title = book.get("metadata", {}).get("title", "Unknown title")
        author = book.get("metadata", {}).get("author", "Unknown author")
        path = book.get("stored_path", "Unknown path")
        fmt = book.get("format", "Unknown format")
        print(f"- {title} by {author}")
        print(f"  Stored Path: {path}")
        print(f"  Format: {fmt}\n")


if __name__ == "__main__":
    index = load_index()

    # Ask user for search criteria
    title = input("Enter title to search (leave blank to skip): ").strip() or None
    author = input("Enter author to search (leave blank to skip): ").strip() or None
    fmt = (
        input("Enter format to filter (epub, pdf, etc., leave blank to skip): ").strip()
        or None
    )

    # Ask user for search mode
    mode = input("Choose search mode ('strict' or 'relaxed'): ").strip().lower()
    if mode not in ("strict", "relaxed"):
        print("Invalid mode, defaulting to 'strict'")
        mode = "strict"

    # Filter library with chosen criteria and mode
    results = filter_library(index, title=title, author=author, fmt=fmt, mode=mode)

    print(f"\nFound {len(results)} books in {mode} mode:")
    display_library(results)
