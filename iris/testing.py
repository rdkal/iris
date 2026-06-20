"""Browser testing support (see DESIGN.md §8).

Two modes:

**Stub mode** — define routes (URL -> component tree) and steps as data; iris
pre-renders each route to a fragment and embeds everything in a self-contained
page.  ``iris-test.js`` intercepts fixi's ``fx:config`` to serve the matching
fragment (no server), runs the steps, and reports pass/fail in-page.  Open the
page in any browser, or drive it with :func:`run_in_browser`.

**Live-app mode** — :func:`collect_errors` attaches to a real Playwright page
(hitting your running app) and records JS exceptions / console errors / fixi
errors / bad status codes.  iris adds no abstraction over Playwright here.

Playwright is an optional extra: ``pip install iris-ui[test]``.
"""

from __future__ import annotations

import contextlib
import json
import socket
import threading
import time
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping

from .assets import fixi_js, iris_fixi_js, iris_test_js
from .core import _example_source, raw, render
from .html import h
from .theme import DARK, Theme, stylesheet

__all__ = [
    "click",
    "fill",
    "expect_text",
    "expect_absent",
    "wait",
    "BrowserTest",
    "browser_test",
    "Result",
    "run_in_browser",
    "collect_errors",
    "live_app",
    "browser_example",
    "BrowserExample",
    "browser_examples",
]


# --- Step helpers (serialized into the page for iris-test.js) ------------- #

def click(selector: str, *, wait: int | None = None) -> dict[str, Any]:
    step: dict[str, Any] = {"click": selector}
    if wait is not None:
        step["wait"] = wait
    return step


def fill(selector: str, value: str) -> dict[str, Any]:
    return {"fill": selector, "value": value}


def expect_text(text: str) -> dict[str, Any]:
    return {"expect_text": text}


def expect_absent(text: str) -> dict[str, Any]:
    return {"expect_absent": text}


def wait(ms: int) -> dict[str, Any]:
    return {"wait": ms}


def _json(data: Any) -> Any:
    # Escape "</" so embedded fragments can't terminate the <script> early.
    return raw(json.dumps(data).replace("</", "<\\/"))


@dataclass
class BrowserTest:
    """A self-contained stub-mode test page."""

    html: str

    def write(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.html, encoding="utf-8")
        return p


def browser_test(
    view: Any,
    *,
    routes: Mapping[str, Any] | None = None,
    steps: Iterable[Mapping[str, Any]] | None = None,
    theme: Theme = DARK,
    title: str = "iris test",
) -> BrowserTest:
    """Build a stub-mode test page.

    ``view`` is the initial component tree; ``routes`` maps a fixi URL to the
    component tree returned for it (pre-rendered to a fragment); ``steps`` is a
    list of step dicts (see :func:`click`, :func:`expect_text`, ...).
    """

    fragments = {url: render(node) for url, node in (routes or {}).items()}
    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
        ],
        h.body(".iris")[
            view,
            h.script(type="application/json", id="iris-routes")[_json(fragments)],
            h.script(type="application/json", id="iris-steps")[_json(list(steps or []))],
            h.script[fixi_js()],
            h.script[iris_fixi_js()],
            h.script[iris_test_js()],
        ],
    ]
    return BrowserTest(str(document))


# --- Playwright driver ---------------------------------------------------- #

@dataclass
class Result:
    passed: bool
    failures: list[str] = field(default_factory=list)

    def assert_ok(self) -> None:
        assert self.passed, "iris browser test failed:\n  - " + "\n  - ".join(self.failures)


def run_in_browser(test: BrowserTest | str, *, timeout: int = 5000) -> Result:
    """Run a stub-mode page in headless Chromium and return its in-page result."""

    from playwright.sync_api import sync_playwright

    html = test.html if isinstance(test, BrowserTest) else test
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.wait_for_function("window.__iris_test && window.__iris_test.done", timeout=timeout)
            data = page.evaluate("window.__iris_test")
        finally:
            browser.close()
    return Result(bool(data["passed"]), list(data["failures"]))


# --- Browser-test registry (shared by pytest and the docs gallery) ------- #

@dataclass
class BrowserExample:
    """A registered browser test that doubles as gallery documentation."""

    title: str
    func: Callable[[], BrowserTest]

    @cached_property
    def test(self) -> BrowserTest:
        return self.func()

    @property
    def source(self) -> str:
        """The Python that produced the test (the body of the example)."""

        return _example_source(self.func)


_BROWSER_EXAMPLES: list[BrowserExample] = []


def browser_example(title: str | None = None) -> Callable[[Callable[[], BrowserTest]], Callable[[], BrowserTest]]:
    """Register a browser test for both pytest and the docs gallery.

    The decorated function takes no arguments and returns a :func:`browser_test`::

        @browser_example("Tab navigation")
        def _():
            return browser_test(view=..., routes={...}, steps=[...])
    """

    def decorator(func: Callable[[], BrowserTest]) -> Callable[[], BrowserTest]:
        _BROWSER_EXAMPLES.append(BrowserExample(title or func.__name__, func))
        return func

    return decorator


def browser_examples() -> list[BrowserExample]:
    """All registered browser examples, in definition order."""

    return list(_BROWSER_EXAMPLES)


class collect_errors:
    """Attach to a real Playwright ``page`` and record failures.

    Records uncaught JS exceptions, ``console.error``, fixi ``fx:error`` events,
    and responses with a disallowed status code.  Call :meth:`assert_none`.
    """

    def __init__(self, page: Any, *, fail_on_status: Iterable[int] = range(400, 600)):
        self.entries: list[str] = []
        statuses = set(fail_on_status)
        page.add_init_script(
            "addEventListener('fx:error', (e) => "
            "console.error('fx:error', e.detail && e.detail.error));"
        )
        page.on("pageerror", lambda exc: self.entries.append(f"pageerror: {exc}"))
        page.on(
            "console",
            lambda msg: msg.type == "error" and self.entries.append(f"console.error: {msg.text}"),
        )
        page.on(
            "response",
            lambda resp: resp.status in statuses
            and self.entries.append(f"{resp.status} {resp.url}"),
        )

    def assert_none(self) -> None:
        assert not self.entries, "page errors:\n  - " + "\n  - ".join(self.entries)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def live_app(app: Any, *, host: str = "127.0.0.1") -> Iterator[str]:
    """Run an ASGI app (e.g. FastAPI) on a free port for the duration of the block.

    Yields the base URL so a browser can hit real routes (the live-app testing
    mode — exercises fixi swaps against your actual server)::

        with live_app(app) as base_url:
            page.goto(base_url)
    """

    import uvicorn

    port = _free_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host=host, port=port, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time.time() + 10
        while not server.started and time.time() < deadline:
            time.sleep(0.02)
        if not server.started:
            raise RuntimeError("live_app: server failed to start")
        yield f"http://{host}:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)
