"""Pytest plugin: convenience fixtures for iris browser tests.

Auto-loaded via the ``pytest11`` entry point when iris is installed, so tests can
just request the fixtures. All of them skip cleanly when Playwright/Chromium
aren't available, so a plain ``pip install -e .`` (no browser) still collects.

- ``iris_browser`` — a headless Chromium ``Browser`` for the test.
- ``iris_page``    — a fresh Playwright ``Page`` per test.
- ``iris_errors``  — a ``collect_errors`` attached to ``iris_page``.
- ``iris_run``     — run a stub ``browser_test`` and return its ``Result``.

The browser is function-scoped so it never holds a long-lived ``sync_playwright``
across the session — that keeps these fixtures safe to mix with tests that open
their own ``sync_playwright``.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def iris_browser():
    """A headless Chromium browser for the duration of one test (skips if
    Playwright/Chromium are unavailable)."""

    sync_api = pytest.importorskip("playwright.sync_api")
    try:
        pw = sync_api.sync_playwright().start()
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Playwright unavailable: {exc}")
    try:
        browser = pw.chromium.launch()
    except Exception as exc:  # pragma: no cover - browser not installed
        pw.stop()
        pytest.skip(
            "Chromium unavailable — run `python -m playwright install chromium` "
            f"({exc})"
        )
    try:
        yield browser
    finally:
        browser.close()
        pw.stop()


@pytest.fixture
def iris_page(iris_browser):
    """A fresh Playwright page per test (own context, cleaned up after)."""

    context = iris_browser.new_context()
    page = context.new_page()
    try:
        yield page
    finally:
        context.close()


@pytest.fixture
def iris_errors(iris_page):
    """A ``collect_errors`` attached to ``iris_page`` (call ``.assert_none()``)."""

    from .testing import collect_errors

    return collect_errors(iris_page)


@pytest.fixture
def iris_run(iris_browser):
    """Run a stub ``browser_test`` on the shared browser and return its Result.

    Faster than :func:`iris.testing.run_in_browser` across many tests since it
    reuses one browser::

        def test_it(iris_run):
            iris_run(browser_test(...)).assert_ok()
    """

    from .testing import BrowserTest, Result

    def run(test: "BrowserTest | str", *, timeout: int = 5000) -> "Result":
        html = test.html if isinstance(test, BrowserTest) else test
        page = iris_browser.new_page()
        try:
            page.set_content(html, wait_until="load")
            page.wait_for_function(
                "window.__iris_test && window.__iris_test.done", timeout=timeout
            )
            data = page.evaluate("window.__iris_test")
        finally:
            page.close()
        return Result(bool(data["passed"]), list(data["failures"]))

    return run
