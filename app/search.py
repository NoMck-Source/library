from typing import Dict, List, Optional

from .utils import load_index, save_index


def strict_search_library(index: List[Dict], query: str) -> List[Dict]:
    """Simple strict search: matches query as substring in title or author."""
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
    """Relaxed search: matches all words in the needle anywhere in the haystack."""
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
    """Return books that match filters. Title/author match using OR logic."""

    def cmp(haystack: str, needle: str) -> bool:
        if mode == "strict":
            return needle.lower() in haystack.lower()
        else:
            return relaxed_search_library(haystack, needle)

    results = []
    for book in index:
        md = book.get("metadata", {})

        # Check title and author using OR
        matches = False
        if title and md.get("title") and cmp(md["title"], title):
            matches = True
        if author and md.get("author") and cmp(md["author"], author):
            matches = True
        if fmt and md.get("format") and fmt.lower() != md["format"].lower():
            continue  # format must match exactly

        # Include if it matched any query or if no query provided
        if matches or (not title and not author):
            results.append(book)

    return results


def display_library(index: List[Dict]) -> None:
    """Print library entries nicely."""
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

    # Example usage: filter by title, author, and format
    results = filter_library(index, title="dune", author="herbert", mode="relaxed")
    print(f"Found {len(results)} books:")
    display_library(results)
