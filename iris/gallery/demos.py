"""Browser-test examples demonstrating fixi interactions.

Each ``@browser_example`` is a real test (run by pytest via ``run_in_browser``)
*and* a doc panel on the tests gallery page — a live iframe plus the source.
The source is written with short lines so it stays readable in the browser.
"""

from __future__ import annotations

from ..components import AppShell, Banner, Button, Card, List, Tab
from ..html import h
from ..testing import browser_example, browser_test, click, expect_absent, expect_text


@browser_example("Tab navigation")
def _():
    return browser_test(
        view=AppShell(
            active="Home",
            tabs=[
                Tab("Home", "/home"),
                Tab("Search", "/search"),
            ],
        )[h.p["Home view"]],
        routes={"/search": h.p["Search results"]},
        steps=[
            expect_text("Home view"),
            click("a[fx-action='/search']"),
            expect_text("Search results"),
        ],
    )


@browser_example("Lazy load (innerHTML)")
def _():
    return browser_test(
        view=h.div[
            h.div("#panel")[
                h.p(".muted")["Nothing loaded yet."]
            ],
            Button(
                fx_action="/content",
                fx_target="#panel",
                fx_swap="innerHTML",
            )["Load content"],
        ],
        routes={
            "/content": Card[
                h.h3["Loaded!"],
                h.p["Came from the (stub) server."],
            ]
        },
        steps=[
            expect_text("Nothing loaded yet."),
            click("button"),
            expect_text("Loaded!"),
        ],
    )


@browser_example("Optimistic toggle (outerHTML)")
def _():
    return browser_test(
        view=Button(
            fx_action="/like",
            fx_swap="outerHTML",
        )["♡ Like"],
        routes={
            "/like": Button(
                ".primary", disabled=True
            )["♥ Liked"]
        },
        steps=[
            expect_text("♡ Like"),
            click("button"),
            expect_text("♥ Liked"),
            expect_absent("♡ Like"),
        ],
    )


@browser_example("Load more (append)")
def _():
    return browser_test(
        view=h.div[
            List(
                id="items",
                items=["Item 1", "Item 2"],
            ),
            Button(
                fx_action="/more",
                fx_target="#items",
                fx_swap="beforeend",
            )["Load more"],
        ],
        routes={
            "/more": h.fragment[
                h.li["Item 3"],
                h.li["Item 4"],
            ]
        },
        steps=[
            expect_text("Item 2"),
            expect_absent("Item 4"),
            click("button"),
            expect_text("Item 4"),
        ],
    )


@browser_example("Form submit")
def _():
    return browser_test(
        view=h.form(
            fx_action="/submit",
            fx_method="post",
            fx_target="#result",
            fx_swap="innerHTML",
        )[
            h.input(
                name="email",
                placeholder="you@example.com",
            ),
            Button(".primary", type="submit")[
                "Sign up"
            ],
            h.div("#result"),
        ],
        routes={
            "/submit": Banner(".success")[
                "Thanks for signing up!"
            ]
        },
        steps=[
            click("button[type=submit]"),
            expect_text("Thanks for signing up!"),
        ],
    )
