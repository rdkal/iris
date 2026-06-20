"""Framework integration examples shown on the ``frameworks.html`` docs page.

Code-only snippets (no framework import needed to build the gallery).  Only
FastAPI for now; add a new framework by appending ``FrameworkExample``s.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FrameworkExample", "FRAMEWORK_EXAMPLES"]


@dataclass(frozen=True)
class FrameworkExample:
    framework: str
    title: str
    description: str
    code: str


FRAMEWORK_EXAMPLES: list[FrameworkExample] = [
    FrameworkExample(
        "FastAPI",
        "Install",
        "iris owns the view; FastAPI owns routing. Install from GitHub with the "
        "``fastapi`` extra (fastapi + uvicorn).",
        'pip install "iris-ui[fastapi] @ '
        'git+https://github.com/rdkal/iris.git@v0.1.0"',
    ),
    FrameworkExample(
        "FastAPI",
        "Render a page",
        "Return an ``IrisResponse`` — it renders the node and streams it as "
        "``text/html`` (low time-to-first-byte via htpy's chunked rendering).",
        '''from fastapi import FastAPI
from iris import Page, Container, h
from iris.integrations.fastapi import IrisResponse

app = FastAPI()


@app.get("/")
def home() -> IrisResponse:
    return IrisResponse(
        Page(title="Home")[
            Container[h.h1["Hello from iris"]]
        ]
    )''',
    ),
    FrameworkExample(
        "FastAPI",
        "App shell with fixi swaps",
        "``Page(fixi=True)`` inlines fixi. Use ``is_fx(request.headers)`` to "
        "return a bare fragment for a fixi swap, or the full page on a direct "
        "visit — from the *same* view function.",
        '''from fastapi import FastAPI, Request
from iris import Page, AppShell, Tab, is_fx, h
from iris.integrations.fastapi import IrisResponse

app = FastAPI()
TABS = [Tab("Home", "/home"), Tab("Search", "/search")]


def shell(active, view):
    return Page(title="iris", fixi=True)[
        AppShell(title="iris", active=active, tabs=TABS)[view]
    ]


@app.get("/")
def index() -> IrisResponse:
    return IrisResponse(shell("Home", h.p["Welcome home."]))


@app.get("/search")
def search(request: Request) -> IrisResponse:
    view = h.p["Search results"]
    if is_fx(request.headers):
        return IrisResponse(view)          # fragment for the swap
    return IrisResponse(shell("Search", view))  # full page''',
    ),
    FrameworkExample(
        "FastAPI",
        "Handle a form POST",
        "A ``<form>`` with ``fx_*`` attributes posts via fixi; return the "
        "fragment to swap in. No special machinery — just htpy + fixi.",
        '''from fastapi import FastAPI, Form
from iris import Banner
from iris.integrations.fastapi import IrisResponse

app = FastAPI()


@app.post("/signup")
def signup(email: str = Form(...)) -> IrisResponse:
    # validate / persist ...
    return IrisResponse(
        Banner(".success")[f"Thanks, {email}!"]
    )''',
    ),
]
