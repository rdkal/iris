"""iris.ask: form generation from a Pydantic model + the 422 -> field mapping."""

from __future__ import annotations

from typing import Literal

import pytest

pytest.importorskip("pydantic")

from pydantic import BaseModel  # noqa: E402

from iris import ask, render  # noqa: E402


class Signup(BaseModel):
    email: str
    password: str
    role: Literal["admin", "user"] = "user"
    subscribe: bool = False


# --- Form generation (no browser) --------------------------------------- #

def test_form_maps_fields_to_inputs():
    html = render(ask.form(Signup, action="/signup"))
    assert 'class="form"' in html and 'fx-action="/signup"' in html
    assert "novalidate" in html
    assert 'name="email" type="email"' in html
    assert 'name="password" type="password"' in html
    assert "<select" in html and 'name="role"' in html
    assert 'type="checkbox" name="subscribe"' in html
    assert 'type="submit"' in html


def test_form_target_and_values():
    html = render(ask.form(Signup, action="/x", target="#out", swap="innerHTML",
                           values={"email": "a@b.com"}))
    assert 'fx-target="#out"' in html and 'fx-swap="innerHTML"' in html
    assert 'value="a@b.com"' in html


# --- End to end: real FastAPI 422 -> iris-ask.js marks the field --------- #

pytest.importorskip("fastapi")
pytest.importorskip("multipart")  # python-multipart, for Form() handling
pytest.importorskip("playwright.sync_api")

from typing import Annotated  # noqa: E402

from fastapi import FastAPI, Form  # noqa: E402

from iris import Banner, Container, Page, h  # noqa: E402
from iris.integrations.fastapi import IrisResponse  # noqa: E402


# Defined at module scope so FastAPI can resolve the (stringified) annotations.
class Account(BaseModel):
    email: str
    age: int


_app = FastAPI()


@_app.get("/")
def _index() -> IrisResponse:
    return IrisResponse(
        Page(title="Signup", fixi=True)[
            Container[
                ask.form(Account, action="/signup", target="#result", swap="innerHTML"),
                h.div(id="result"),
            ]
        ]
    )


@_app.post("/signup")
def _signup(data: Annotated[Account, Form()]) -> IrisResponse:
    return IrisResponse(Banner(".success")[f"Welcome, {data.email}"])


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
def test_validation_error_marks_field():
    from playwright.sync_api import sync_playwright

    from iris.testing import live_app

    with live_app(_app) as base, sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            page = b.new_page()
            page.goto(base, wait_until="load")
            page.fill('[name="email"]', "a@b.com")  # leave age empty -> 422
            page.click('button[type="submit"]')
            page.wait_for_selector(".field.invalid")
            # the invalid field is age, with an error message, and no success swap
            invalid = page.locator(".field.invalid")
            assert invalid.locator('[name="age"]').count() == 1
            assert invalid.locator(".field-error").inner_text().strip() != ""
            assert "Welcome" not in page.inner_text("body")
        finally:
            b.close()


@browser
def test_valid_submit_swaps_success():
    from playwright.sync_api import sync_playwright

    from iris.testing import live_app

    with live_app(_app) as base, sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            page = b.new_page()
            page.goto(base, wait_until="load")
            page.fill('[name="email"]', "a@b.com")
            page.fill('[name="age"]', "30")
            page.click('button[type="submit"]')
            page.wait_for_selector("text=Welcome, a@b.com")
            assert page.locator(".field.invalid").count() == 0
        finally:
            b.close()


def test_signup_via_fixtures(iris_page, iris_errors):
    # mirrors the "Full app" example on the pytest docs page
    from iris.testing import live_app

    with live_app(_app) as base_url:
        iris_page.goto(base_url, wait_until="load")
        iris_page.fill('[name="email"]', "a@b.com")
        iris_page.fill('[name="age"]', "30")
        iris_page.click('button[type="submit"]')
        iris_page.wait_for_selector("text=Welcome, a@b.com")
    iris_errors.assert_none()
