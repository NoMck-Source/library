from asyncio.unix_events import SelectorEventLoop

from app.utils import save_to_cache, search_hardcover


def fetch(library):
    """
    Let the user select a book from their local library and fetch metadata from Hardcover.

    Args:
        library (list[dict]): List of user's books, each dict should have 'title' and optional 'author'

    Returns:
        dict: The selected book's metadata from Hardcover
    """
    print("Your Library:\n")
    for idx, book in enumerate(library):
        author_str = f" by {book['author']}" if "author" in book else ""
        print(f"{idx + 1}. {book['title']}{author_str}")

    choice = input("\nSelect a book number to fetch metaata: ")
    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(library):
            raise ValueError()
    except ValueError:
        print("Invalid selection. Try again.")
        return None

    selected_book = library[choice_idx]
    query = f"{selected_book['title']} {selected_book.get('author', '')}".strip()

    print(f"\nSearching Hardcover for: {query}")
    results = search_hardcover(query)

    if not results:
        print("No results found.")
        return None

    print("\nSelect the correct edition from Hardcover:")
    for idx, result in enumerate(results):
        authors = ", ".join(result.get("authors", []))
        print(f"{idx + 1}. {result['title']} by {authors}")

    edition_choice = input("\nEnter the number of the correct edition: ")
    try:
        edition_idx = int(edition_choice) - 1
        if edition_idx < 0 or edition_idx >= len(results):
            raise ValueError()
    except ValueError:
        print("Invalid selection. Using result 1.")
        edition_idx = 0

    selected_metadata = results[edition_idx]

    save_to_cache(selected_metadata)

    return selected_metadata
