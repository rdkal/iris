"""A tiny FastAPI reference app for iris.

Run it::

    pip install "iris-ui[fastapi]"
    uvicorn examples.fastapi_app:app --reload

Then open http://127.0.0.1:8000 — tapping a tab swaps the main region via fixi
(the same view function returns a full page on a direct visit and a bare
fragment for the swap, switched on ``is_fx``).
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from iris import AppShell, Card, Page, Stack, Tab, h, is_fx
from iris.integrations.fastapi import IrisResponse

app = FastAPI()

TABS = [
    Tab("Home", "/home", icon="●"),
    Tab("Search", "/search", icon="○"),
    Tab("Profile", "/me", icon="◐"),
]

VIEWS = {
    "Home": ("/home", h.p["Welcome to iris."]),
    "Search": ("/search", Stack(gap=2)[h.h2["Search"], Card[h.p["No results yet."]]]),
    "Profile": ("/me", Stack(gap=2)[h.h2["Profile"], h.p(".muted")["jockeback91@…"]]),
}


def _shell(active: str, view: object) -> object:
    return Page(title="iris", fixi=True)[
        AppShell(title="iris", active=active, tabs=TABS)[view]
    ]


def _route(active: str):
    def handler(request: Request) -> IrisResponse:
        _, view = VIEWS[active]
        if is_fx(request.headers):
            return IrisResponse(view)          # fragment for the fixi swap
        return IrisResponse(_shell(active, view))  # full page on a direct visit

    return handler


@app.get("/")
def index() -> IrisResponse:
    return IrisResponse(_shell("Home", VIEWS["Home"][1]))


for _active, (_path, _view) in VIEWS.items():
    app.get(_path)(_route(_active))
