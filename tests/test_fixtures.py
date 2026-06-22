"""The iris pytest plugin fixtures (auto-loaded via the pytest11 entry point)."""

from __future__ import annotations

import pytest

from iris import Button, Page, h, render
from iris.testing import browser_test, click, expect_text, live_app

pytest.importorskip("playwright.sync_api")


def test_iris_run_runs_a_stub_test(iris_run):
    test = browser_test(
        view=h.div[
            h.div("#out")["initial"],
            Button(fx_action="/next", fx_target="#out", fx_swap="innerHTML")["Load"],
        ],
        routes={"/next": h.p["swapped"]},
        steps=[click("button"), expect_text("swapped")],
    )
    iris_run(test).assert_ok()


def test_iris_run_reports_failure(iris_run):
    result = iris_run(browser_test(view=h.div["x"], steps=[expect_text("absent")]))
    assert result.passed is False


def test_iris_page_fixture_loads_content(iris_page):
    iris_page.set_content(render(Page(title="t")[h.p["hello page"]]), wait_until="load")
    assert "hello page" in iris_page.inner_text("body")


async def _hello_asgi(scope, receive, send):
    assert scope["type"] == "http"
    body = render(Page(title="t")[h.p["live hello"]]).encode()
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"text/html; charset=utf-8")]})
    await send({"type": "http.response.body", "body": body})


def test_iris_errors_with_live_app(iris_page, iris_errors):
    pytest.importorskip("uvicorn")
    with live_app(_hello_asgi) as base_url:
        iris_page.goto(base_url, wait_until="load")
        assert "live hello" in iris_page.inner_text("body")
    iris_errors.assert_none()
