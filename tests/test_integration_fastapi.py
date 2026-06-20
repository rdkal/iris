"""FastAPI integration: IrisResponse, is_fx fragment-vs-page, and live_app."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from iris import AppShell, Page, Tab, h, is_fx  # noqa: E402
from iris.integrations.fastapi import IrisResponse  # noqa: E402

TABS = [Tab("Home", "/home"), Tab("Search", "/search")]


def _shell(active, view):
    return Page(title="iris", fixi=True)[
        AppShell(title="iris", active=active, tabs=TABS)[view]
    ]


def make_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def index() -> IrisResponse:
        return IrisResponse(_shell("Home", h.p["Home view"]))

    @app.get("/search")
    def search(request: Request) -> IrisResponse:
        view = h.p["Search results"]
        if is_fx(request.headers):
            return IrisResponse(view)
        return IrisResponse(_shell("Search", view))

    return app


def test_iris_response_renders_full_html_page():
    client = TestClient(make_app())
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert body.lower().startswith("<!doctype html>")
    assert "Home view" in body and 'class="appshell"' in body


def test_is_fx_returns_fragment_vs_full_page():
    client = TestClient(make_app())

    full = client.get("/search").text
    assert "<html" in full and "Search results" in full

    fragment = client.get("/search", headers={"FX-Request": "true"}).text
    assert fragment == "<p>Search results</p>"
    assert "<html" not in fragment


# --- Live-app mode (real server + browser) ------------------------------- #

pytest.importorskip("playwright.sync_api")
pytest.importorskip("uvicorn")


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch().close()
        return True
    except Exception:
        return False


browser = pytest.mark.skipif(not _chromium_available(), reason="Chromium not installed")


@browser
def test_live_app_tab_swap_end_to_end():
    from playwright.sync_api import sync_playwright

    from iris.testing import collect_errors, live_app

    app = make_app()
    with live_app(app) as base_url, sync_playwright() as pw:
        browser_ = pw.chromium.launch()
        try:
            page = browser_.new_page()
            errors = collect_errors(page)
            page.goto(base_url, wait_until="load")
            assert "Home view" in page.inner_text("body")
            page.click("a[fx-action='/search']")
            page.wait_for_selector("text=Search results")
            errors.assert_none()
        finally:
            browser_.close()
