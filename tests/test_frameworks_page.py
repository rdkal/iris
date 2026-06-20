"""Tests for the frameworks docs page."""

from __future__ import annotations

from iris.gallery import render_frameworks


def test_render_frameworks_has_fastapi_examples():
    html = render_frameworks()
    assert html.lower().startswith("<!doctype html>")
    assert 'id="fastapi"' in html
    assert "IrisResponse" in html
    assert "is_fx" in html
    assert "panel-note" in html  # descriptions render


def test_frameworks_page_cross_links():
    html = render_frameworks()
    assert 'href="index.html"' in html
    assert 'href="tests.html"' in html
