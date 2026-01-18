from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.search import filter_library
from app.utils import load_index

app = FastAPI()

# Templates folder
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, query: str = ""):
    index = load_index()
    if query:
        # Search in both title and author using relaxed mode
        results = filter_library(index, title=query, author=query, mode="relaxed")
    else:
        results = index

    return templates.TemplateResponse(
        "index.html", {"request": request, "books": results, "query": query}
    )
