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


def test_demo_source_lines_stay_short():
    # the displayed test code should read well in a narrow viewport
    for ex in browser_examples():
        for line in ex.source.splitlines():
            assert len(line) <= 60, f"{ex.title}: {line!r}"


def test_render_tests_embeds_iframes_and_source():
    html = render_tests()
    assert html.lower().startswith("<!doctype html>")
    assert "test-frame" in html and "srcdoc=" in html
    assert 'href="index.html"' in html  # back-link to the gallery
    # the full test source (which includes the routes) is shown
    assert "browser_test(" in html
    assert "Search results" in html


# --- Browser: every demo is a passing test (via the iris_run fixture) ---- #

@pytest.mark.parametrize("example", browser_examples(), ids=lambda e: e.title)
def test_demo_passes_in_browser(example, iris_run):
    iris_run(example.test).assert_ok()
