import json
import os
from pathlib import Path

import dotenv
import requests

DEFAULT_LIBRARY_ROOT = Path(os.environ.get("LIBRARY_ROOT", "library_files"))
INDEX_FILE = DEFAULT_LIBRARY_ROOT / "library_index.json"
CACHE_DIR = Path("app/hardcover_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = CACHE_DIR / "metadata.json"
###
dotenv.load_dotenv()
HARD_COVER_TOKEN = os.environ.get("HARDCOVER_TOKEN")
API_URL = "https://api.hardcover.app/v1/graphql"
HEADERS = {
    "Authorization": f"Bearer {HARD_COVER_TOKEN}",
    "Content-Type": "application/json",
}


#
#
#
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


#
#
#
def load_cache():
    # Load metadata cache
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_to_cache(key, metadata):
    # Save metadata to cache
    cache = load_cache()
    cache[key] = metadata
    with open(METADATA_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Cached metadata for {metadata.get('title')}")


#
#
#


def search_hardcover(query, per_page=25, page=1):
    graphql_query = {
        "query": f"""
        query {{
            search(query: "{query}", page: {page}, per_page: {per_page}) {{
                error
                page
                per_page
                query
                query_type
                results
            }}
        }}
        """
    }

    resp = requests.post(API_URL, headers=HEADERS, json=graphql_query)

    if resp.status_code != 200:
        print(f"Status: {resp.status_code}")
        print(resp.text)
        return []

    data = resp.json()
    search_data = data.get("data", {}).get("search", {})

    if search_data.get("error"):
        print("Error:", search_data["error"])
        return []

    # results comes back as JSON string, parse it
    results_json = search_data.get("results")
    if isinstance(results_json, str):
        results = json.loads(results_json)
    else:
        results = results_json

    hits = results.get("hits", [])
    books = []

    for hit in hits:
        doc = hit.get("document", {})
        books.append(
            {
                "title": doc.get("title"),
                "authors": doc.get("author_names"),
                "slug": doc.get("slug"),
                "isbns": doc.get("isbns"),
                "release_date": doc.get("release_date"),
                "has_ebook": doc.get("has_ebook"),
                "has_audiobook": doc.get("has_audiobook"),
                "cover_url": doc.get("image", {}).get("url"),
            }
        )

    return books


if __name__ == "__main__":
    queries = ["Dune Frank Herbert", "The Eye of the Bedlam Bride Matt Dinniman"]

    for q in queries:
        print(f"\nSearching Hardcover for: {q}")
        books = search_hardcover(q)
        if not books:
            print("No results found")
        for b in books:
            print(b["title"], "-", ", ".join(b["authors"]))
