"""Tests for iris.testing — stub-page assembly and (browser) end-to-end runs."""

from __future__ import annotations

import json

import pytest

from iris import Button, Tab, h
from iris.testing import (
    browser_test,
    click,
    expect_absent,
    expect_text,
    fill,
    wait,
)


# --- Step helpers (no browser) ------------------------------------------- #

def test_step_helpers():
    assert click("button") == {"click": "button"}
    assert click("button", wait=10) == {"click": "button", "wait": 10}
    assert fill("#email", "a@b.com") == {"fill": "#email", "value": "a@b.com"}
    assert expect_text("hi") == {"expect_text": "hi"}
    assert expect_absent("bye") == {"expect_absent": "bye"}
    assert wait(50) == {"wait": 50}


# --- Stub page assembly (no browser) ------------------------------------- #

def test_browser_test_embeds_routes_steps_and_scripts():
    t = browser_test(
        view=h.div["start"],
        routes={"/next": h.p["done"]},
        steps=[click("button"), expect_text("done")],
    )
    html = t.html
    assert 'id="iris-routes"' in html and 'id="iris-steps"' in html
    assert "start" in html
    # the three scripts are inlined
    assert "__fixi_mo" in html and "__iris_fixi" in html and "iris-routes" in html
    # route fragment is embedded as JSON with </ escaped so it can't close <script>
    assert '"/next"' in html
    assert "<\\/p>" in html


def test_browser_test_write(tmp_path):
    t = browser_test(view=h.div["x"])
    out = t.write(tmp_path / "t.html")
    assert out.exists() and "iris-routes" in out.read_text(encoding="utf-8")


# --- Browser end-to-end (needs Playwright + Chromium) -------------------- #

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
def test_stub_click_triggers_fixi_swap():
    from iris.testing import run_in_browser

    view = h.div[
        h.div("#out")["initial"],
        Button(fx_action="/next", fx_target="#out", fx_swap="innerHTML")["Load"],
    ]
    result = run_in_browser(
        browser_test(
            view=view,
            routes={"/next": h.p["swapped content"]},
            steps=[
                expect_text("initial"),
                click("button"),
                expect_text("swapped content"),
                expect_absent("initial"),
            ],
        )
    )
    result.assert_ok()


@browser
def test_stub_failure_is_reported():
    from iris.testing import run_in_browser

    result = run_in_browser(browser_test(view=h.div["x"], steps=[expect_text("absent")]))
    assert result.passed is False
    assert any("expect_text" in f for f in result.failures)


@browser
def test_appshell_tab_swaps_main():
    from iris import AppShell
    from iris.testing import run_in_browser

    view = AppShell(active="Home", tabs=[Tab("Home", "/home"), Tab("Search", "/search")])[
        h.p["home view"]
    ]
    result = run_in_browser(
        browser_test(
            view=view,
            routes={"/search": h.p["search results"]},
            steps=[
                expect_text("home view"),
                click("a[fx-action='/search']"),
                expect_text("search results"),
            ],
        )
    )
    result.assert_ok()


@browser
def test_gallery_has_no_js_errors():
    from iris.gallery import render_gallery
    from iris.testing import collect_errors
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            page = b.new_page()
            errs = collect_errors(page)
            page.set_content(render_gallery(), wait_until="load")
            page.click("#theme-toggle")
            page.wait_for_timeout(100)
            errs.assert_none()
        finally:
            b.close()
