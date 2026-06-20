"""The browser-example demos double as the suite's interaction tests."""

from __future__ import annotations

import pytest

import iris.gallery.demos  # noqa: F401  (registers the browser examples)
from iris.gallery import render_tests
from iris.testing import browser_examples


# --- No browser: registry + tests-page assembly -------------------------- #

def test_demos_are_registered():
    titles = [ex.title for ex in browser_examples()]
    assert "Tab navigation" in titles
    assert len(titles) >= 5


def test_each_demo_parses_routes_as_source():
    for ex in browser_examples():
        assert ex.routes, f"{ex.title} has no parsed routes"
        for url, source in ex.routes.items():
            assert url.startswith("/")
            assert source.strip()


def test_render_tests_embeds_iframes_routes_and_source():
    html = render_tests()
    assert html.lower().startswith("<!doctype html>")
    assert "test-frame" in html and "srcdoc=" in html
    assert 'href="index.html"' in html  # back-link to the gallery
    assert "routes (URL" in html
    # a known route source appears in a code block
    assert "Search results" in html


# --- Browser: every demo is a passing test ------------------------------- #

pytest.importorskip("playwright.sync_api")


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
@pytest.mark.parametrize("example", browser_examples(), ids=lambda e: e.title)
def test_demo_passes_in_browser(example):
    from iris.testing import run_in_browser

    run_in_browser(example.test).assert_ok()
