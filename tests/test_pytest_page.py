"""Tests for the pytest docs page."""

from __future__ import annotations

from iris.gallery import render_pytest


def test_render_pytest_has_prereqs_and_examples():
    html = render_pytest()
    assert html.lower().startswith("<!doctype html>")
    assert "hero-title" in html
    assert "playwright install chromium" in html  # prerequisites
    # both testing modes are documented
    assert "iris_run" in html and "browser_test(" in html       # browser-only
    assert "live_app" in html and "iris_errors" in html         # full app
    assert "Annotated[Signup, Form()]" in html
    # no-browser render check
    assert "def test_button_has_action" in html


def test_pytest_page_cross_links():
    html = render_pytest()
    assert 'href="index.html"' in html
    assert 'href="ask.html"' in html
