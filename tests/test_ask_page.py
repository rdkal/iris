"""Tests for the ask docs page."""

from __future__ import annotations

from iris.gallery import render_ask


def test_render_ask_has_examples_and_preview():
    html = render_ask()
    assert html.lower().startswith("<!doctype html>")
    assert "iris · ask" in html
    assert "ask.form(" in html
    assert "Annotated[Signup, Form()]" in html
    assert 'class="form"' in html          # live preview form
    assert "field invalid" in html          # invalid-state preview
    assert "iris-ask.js" in html


def test_ask_page_cross_links():
    html = render_ask()
    assert 'href="index.html"' in html
    assert 'href="frameworks.html"' in html
