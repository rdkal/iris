"""Render the component gallery to a self-contained static HTML page."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Importing the package registers every component's examples; importing demos
# registers the browser-test examples shown on the tests page.
import iris  # noqa: F401
from . import demos  # noqa: F401
from ..components import Button, Checkbox, Field, Form, Input, Select
from ..core import Component, Example, classes, raw, registered_components
from ..html import h
from ..testing import BrowserExample, browser_examples
from ..theme import DARK, Theme, stylesheet
from .frameworks import FRAMEWORK_EXAMPLES, FrameworkExample

__all__ = [
    "render_gallery", "render_tests", "render_frameworks", "render_ask",
    "render_pytest", "build",
]

_PAGES = [
    ("index.html", "Components"),
    ("tests.html", "Tests"),
    ("frameworks.html", "Frameworks"),
    ("ask.html", "Ask"),
    ("pytest.html", "pytest"),
]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _hero(current: str, subtitle: str) -> Any:
    return h.header(".gallery-hero")[
        h.h1(".hero-title")["iris"],
        h.p(".hero-sub")[subtitle],
        h.nav(".hero-nav")[
            (
                h.a(class_=classes("hero-link", {"active": href == current}), href=href)[label]
                for href, label in _PAGES
            )
        ],
        h.button(".theme-btn", id="theme-toggle", type="button")["Toggle theme"],
    ]


GALLERY_CSS = """
.gallery-main { max-width: 60rem; margin-inline: auto; }

.gallery-hero {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  gap: calc(var(--space) * 2);
  padding: calc(var(--space) * 10) calc(var(--space) * 3) calc(var(--space) * 6);
}
.hero-title {
  font-size: clamp(3rem, 14vw, 6rem); font-weight: 800;
  letter-spacing: -0.03em; line-height: 1;
}
.hero-sub { color: var(--muted); margin: 0; max-width: 34rem; }
.hero-nav {
  display: flex; flex-direction: column; gap: calc(var(--space) * 1.25);
  width: min(22rem, 100%); margin-top: calc(var(--space) * 2);
}
.hero-link {
  display: block; padding: calc(var(--space) * 1.5) calc(var(--space) * 2);
  border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text); background: var(--surface); font-weight: 500;
}
.hero-link:hover { border-color: var(--accent); text-decoration: none; }
.hero-link.active { border-color: var(--accent); color: var(--accent); }

.theme-btn {
  font-size: 0.85em; padding: 0.3rem 0.8rem;
  border: 1px solid var(--border); border-radius: 0.5rem;
  background: var(--surface); color: var(--text); cursor: pointer;
}

.gallery-index {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
  padding: calc(var(--space) * 2) calc(var(--space) * 3);
}
.gallery-index a {
  font-size: 0.85em; color: var(--muted);
  border: 1px solid var(--border); border-radius: 999px; padding: 0.15rem 0.65rem;
}
.gallery-index a:hover { color: var(--text); text-decoration: none; border-color: var(--accent); }

.component-section { padding: calc(var(--space) * 3); border-top: 1px solid var(--border); scroll-margin-top: 4rem; }
.component-section > h2 { font-size: 1.4rem; }
.component-doc { color: var(--muted); margin: 0.35rem 0 1rem; max-width: 38rem; }
.component-doc code {
  background: color-mix(in oklab, var(--surface), white 6%);
  padding: 0.1em 0.35em; border-radius: 0.35em; font-size: 0.9em; color: var(--text);
}

.panel-card { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; margin-top: 1rem; }
.panel-head {
  padding: 0.6rem 1rem; font-size: 0.78em; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--muted); border-bottom: 1px solid var(--border); background: var(--surface);
}
.panel-preview { padding: calc(var(--space) * 3); }
.panel-note {
  margin: 0; padding: 0.75rem 1rem; color: var(--muted); font-size: 0.9em;
  border-bottom: 1px solid var(--border);
}
.panel-note code {
  background: color-mix(in oklab, var(--surface), white 6%);
  padding: 0.1em 0.35em; border-radius: 0.35em; font-size: 0.9em; color: var(--text);
}

.panel-code { position: relative; border-top: 1px solid var(--border); }
.panel-code pre {
  margin: 0; padding: 1rem; font-size: 0.85em; line-height: 1.5;
  white-space: pre-wrap; overflow-wrap: anywhere;  /* wrap long lines on mobile */
  background: color-mix(in oklab, var(--bg), black 35%);
}
.panel-code .copy {
  position: absolute; top: 0.5rem; right: 0.5rem;
  font-size: 0.75em; padding: 0.2rem 0.6rem;
  border: 1px solid var(--border); border-radius: 0.4rem;
  background: var(--surface); color: var(--muted); cursor: pointer;
}
.panel-code .copy:hover { color: var(--text); }

.header-actions { display: flex; gap: 0.5rem; align-items: center; }

.test-frame {
  width: 100%; height: 340px; display: block;
  border: 0; border-top: 1px solid var(--border); background: var(--bg);
}
"""

SCRIPT = """
document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const code = btn.parentElement.querySelector('code').innerText;
    try { await navigator.clipboard.writeText(code); } catch (e) {}
    const prev = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(() => { btn.textContent = prev; }, 1200);
  });
});
const toggle = document.getElementById('theme-toggle');
if (toggle) {
  toggle.addEventListener('click', () => {
    const root = document.documentElement;
    root.dataset.theme = root.dataset.theme === 'light' ? '' : 'light';
  });
}
"""


_RST_CODE = re.compile(r"``(.+?)``")


def _doc_nodes(text: str) -> list[Any]:
    """Render a component docstring: collapse whitespace and turn RST ``code``
    spans into <code> elements."""

    collapsed = " ".join(text.split())
    nodes: list[Any] = []
    for i, part in enumerate(_RST_CODE.split(collapsed)):
        if not part:
            continue
        nodes.append(h.code[part] if i % 2 else part)
    return nodes


def _panel(example: Example) -> Any:
    return h.article(".panel-card")[
        h.div(".panel-head")[f"{example.component.name} · {example.title}"],
        h.div(".panel-preview")[example.func()],
        h.div(".panel-code")[
            h.button(".copy", type="button", data_copy=True)["Copy"],
            h.pre[h.code[example.source]],
        ],
    ]


def _section(component: Component) -> Any:
    return h.section(".component-section", id=component.name)[
        h.h2[component.name],
        h.p(".component-doc")[_doc_nodes(component.__doc__)] if component.__doc__ else None,
        [_panel(ex) for ex in component.examples],
    ]


def render_gallery(theme: Theme = DARK, *, title: str = "iris — components") -> str:
    components = registered_components()
    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
            h.style[raw(GALLERY_CSS)],
        ],
        h.body(".iris")[
            _hero("index.html", "Live render + the exact source for every component."),
            h.nav(".gallery-index")[
                (h.a(href=f"#{c.name}")[c.name] for c in components)
            ],
            h.main(".gallery-main")[
                (_section(c) for c in components)
            ],
            h.script[raw(SCRIPT)],
        ],
    ]
    return str(document)


def _test_panel(example: BrowserExample) -> Any:
    return h.article(".panel-card", id=_slug(example.title))[
        h.div(".panel-head")[example.title],
        h.iframe(
            ".test-frame",
            srcdoc=example.test.html,
            sandbox="allow-scripts allow-same-origin allow-forms",
            loading="lazy",
        ),
        h.div(".panel-code")[
            h.button(".copy", type="button", data_copy=True)["Copy"],
            h.pre[h.code[example.source]],
        ],
    ]


def render_tests(theme: Theme = DARK, *, title: str = "iris — tests") -> str:
    examples = browser_examples()
    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
            h.style[raw(GALLERY_CSS)],
        ],
        h.body(".iris")[
            _hero("tests.html", "Live fixi interactions — each panel is a real browser test."),
            h.nav(".gallery-index")[
                (h.a(href=f"#{_slug(ex.title)}")[ex.title] for ex in examples)
            ],
            h.main(".gallery-main")[
                (_test_panel(ex) for ex in examples)
            ],
            h.script[raw(SCRIPT)],
        ],
    ]
    return str(document)


def _framework_panel(example: FrameworkExample) -> Any:
    return h.article(".panel-card", id=_slug(f"{example.framework}-{example.title}"))[
        h.div(".panel-head")[example.title],
        h.p(".panel-note")[_doc_nodes(example.description)],
        h.div(".panel-code")[
            h.button(".copy", type="button", data_copy=True)["Copy"],
            h.pre[h.code[example.code]],
        ],
    ]


def render_frameworks(theme: Theme = DARK, *, title: str = "iris — frameworks") -> str:
    frameworks: dict[str, list[FrameworkExample]] = {}
    for example in FRAMEWORK_EXAMPLES:
        frameworks.setdefault(example.framework, []).append(example)

    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
            h.style[raw(GALLERY_CSS)],
        ],
        h.body(".iris")[
            _hero("frameworks.html", "Use iris with your web framework."),
            h.nav(".gallery-index")[
                (h.a(href=f"#{_slug(name)}")[name] for name in frameworks)
            ],
            h.main(".gallery-main")[
                (
                    h.section(".component-section", id=_slug(name))[
                        h.h2[name],
                        [_framework_panel(ex) for ex in examples],
                    ]
                    for name, examples in frameworks.items()
                )
            ],
            h.script[raw(SCRIPT)],
        ],
    ]
    return str(document)


_ASK_MODEL = '''from pydantic import BaseModel
from typing import Literal


class Signup(BaseModel):
    email: str
    password: str
    role: Literal["admin", "user"] = "user"
    subscribe: bool = False'''

_ASK_FORM = '''from iris import ask

ask.form(
    Signup,
    action="/signup",
    target="#result",
    swap="innerHTML",
)'''

_ASK_HANDLER = '''from typing import Annotated
from fastapi import FastAPI, Form
from iris import ask, Banner, Container, Page, h
from iris.integrations.fastapi import IrisResponse

app = FastAPI()


@app.get("/signup")
def signup_form() -> IrisResponse:
    return IrisResponse(
        Page(title="Sign up", fixi=True)[
            Container[
                ask.form(Signup, action="/signup",
                         target="#result", swap="innerHTML"),
                h.div(id="result"),
            ]
        ]
    )


@app.post("/signup")
def signup(data: Annotated[Signup, Form()]) -> IrisResponse:
    # Pydantic validates `data`. On failure FastAPI returns
    # its 422 JSON and iris-ask.js marks the bad fields —
    # no server-side error rendering needed.
    return IrisResponse(
        Banner(".success")[f"Welcome, {data.email}!"]
    )'''


def _ask_preview_form() -> Any:
    return Form(action="/signup")[
        Field(label="Email", name="email")[Input(name="email", type="email")],
        Field(label="Password", name="password")[Input(name="password", type="password")],
        Field(label="Role", name="role")[Select(name="role", options=["admin", "user"])],
        Checkbox(name="subscribe", label="Subscribe to updates"),
        Button(".primary", type="submit")["Sign up"],
    ]


def _ask_invalid_field() -> Any:
    return Field(".invalid", label="Email", name="email",
                 error="value is not a valid email address")[
        Input(name="email", type="email", value="nope")
    ]


def _ask_panel(title: str, note: str, *, preview: Any = None, code: str | None = None) -> Any:
    return h.article(".panel-card", id=_slug(title))[
        h.div(".panel-head")[title],
        h.p(".panel-note")[_doc_nodes(note)],
        h.div(".panel-preview")[preview] if preview is not None else None,
        h.div(".panel-code")[
            h.button(".copy", type="button", data_copy=True)["Copy"],
            h.pre[h.code[code]],
        ] if code is not None else None,
    ]


def render_ask(theme: Theme = DARK, *, title: str = "iris — ask") -> str:
    panels = [
        _ask_panel(
            "What ask is",
            "``iris.ask`` builds a form from a Pydantic model — one ``Field`` + "
            "control per model field, types mapped to input types. It's plain htpy "
            "+ fixi + FastAPI conventions underneath; the model is the single source "
            "of truth for both the form and validation.",
        ),
        _ask_panel("1. Define a model", "A normal Pydantic model.", code=_ASK_MODEL),
        _ask_panel(
            "2. Render the form",
            "``ask.form`` returns a ``<form>`` that posts via fixi. Below is the "
            "rendered result (built from the same form primitives).",
            preview=_ask_preview_form(),
            code=_ASK_FORM,
        ),
        _ask_panel(
            "3. The FastAPI handler",
            "GET renders the form; POST validates with Pydantic. There is **no "
            "server-side error rendering** — FastAPI's default ``422`` carries the "
            "field errors.",
            code=_ASK_HANDLER,
        ),
        _ask_panel(
            "4. Validation errors",
            "``iris-ask.js`` (bundled by ``Page(fixi=True)``) reads FastAPI's 422 "
            "JSON and adds ``.invalid`` + the message to each field by name — "
            "without a swap. The rendered invalid state:",
            preview=_ask_invalid_field(),
        ),
    ]
    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
            h.style[raw(GALLERY_CSS)],
        ],
        h.body(".iris")[
            _hero("ask.html", "Forms from a Pydantic model — convenience over htpy + fixi + FastAPI."),
            h.main(".gallery-main")[panels],
            h.script[raw(SCRIPT)],
        ],
    ]
    return str(document)


_PYTEST_INSTALL = '''# iris with the test extra (pytest, playwright, fastapi, …)
pip install "iris-ui[test] @ git+https://github.com/rdkal/iris.git@v0.1.0"

# download the headless browser Playwright drives (one time)
python -m playwright install chromium'''

_PYTEST_BROWSER = '''from iris import Button, h
from iris.testing import browser_test, click, expect_text


def test_lazy_load(iris_run):
    test = browser_test(
        view=h.div[
            h.div("#out")["empty"],
            Button(fx_action="/content", fx_target="#out",
                   fx_swap="innerHTML")["Load"],
        ],
        routes={"/content": h.p["loaded!"]},
        steps=[
            expect_text("empty"),
            click("button"),
            expect_text("loaded!"),
        ],
    )
    iris_run(test).assert_ok()'''

_PYTEST_APP = '''from typing import Annotated
from fastapi import FastAPI, Form
from pydantic import BaseModel

from iris import ask, Banner, Container, Page, h
from iris.integrations.fastapi import IrisResponse
from iris.testing import live_app


# Model + app at module scope so FastAPI can
# resolve the (stringified) annotations.
class Signup(BaseModel):
    email: str
    age: int


app = FastAPI()


@app.get("/")
def index() -> IrisResponse:
    return IrisResponse(
        Page(title="Sign up", fixi=True)[
            Container[
                ask.form(Signup, action="/signup",
                         target="#result", swap="innerHTML"),
                h.div(id="result"),
            ]
        ]
    )


@app.post("/signup")
def signup(data: Annotated[Signup, Form()]) -> IrisResponse:
    return IrisResponse(
        Banner(".success")[f"Welcome, {data.email}"]
    )


def test_signup(iris_page, iris_errors):
    with live_app(app) as base_url:
        iris_page.goto(base_url)
        iris_page.fill("[name=email]", "a@b.com")
        iris_page.fill("[name=age]", "30")
        iris_page.click("button[type=submit]")
        iris_page.wait_for_selector("text=Welcome, a@b.com")
    iris_errors.assert_none()  # no JS/fixi errors, no bad status'''

_PYTEST_RENDER = '''from iris import render, Button


def test_button_has_action():
    html = render(Button(fx_action="/go")["Go"])
    assert 'fx-action="/go"' in html'''


def render_pytest(theme: Theme = DARK, *, title: str = "iris — pytest") -> str:
    panels = [
        _ask_panel(
            "Prerequisites",
            "iris ships a pytest plugin that auto-loads (via a ``pytest11`` entry "
            "point), so the fixtures below need no ``conftest``. Install the "
            "``test`` extra and the browser; browser tests **skip cleanly** if "
            "Chromium isn't installed.",
            code=_PYTEST_INSTALL,
        ),
        _ask_panel(
            "Fixtures",
            "``iris_run`` — run a stub ``browser_test`` → ``Result``. "
            "``iris_page`` — a fresh Playwright page. "
            "``iris_errors`` — a ``collect_errors`` attached to it "
            "(JS exceptions, ``console.error``, fixi ``fx:error``, bad status). "
            "``iris_browser`` — the underlying Chromium.",
        ),
        _ask_panel(
            "Browser-only (no server)",
            "Define the view, the ``routes`` (URL → component tree) and the "
            "``steps``; iris runs them in the page and reports pass/fail. Ideal "
            "for fixi interactions without a backend.",
            code=_PYTEST_BROWSER,
        ),
        _ask_panel(
            "Full app (FastAPI + live_app)",
            "``live_app`` runs your real ASGI app on a port; drive it with "
            "``iris_page`` (plain Playwright) and assert nothing broke with "
            "``iris_errors``. Put the model + app at **module scope** so FastAPI "
            "can resolve annotations.",
            code=_PYTEST_APP,
        ),
        _ask_panel(
            "No browser needed",
            "Components are pure ``data → HTML`` functions, so the cheapest checks "
            "just call ``render()`` and assert on the string — no fixtures, no "
            "browser.",
            code=_PYTEST_RENDER,
        ),
    ]
    document = h.html(lang="en")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title],
            h.style[raw(stylesheet(theme))],
            h.style[raw(GALLERY_CSS)],
        ],
        h.body(".iris")[
            _hero("pytest.html", "Test your iris pages with pytest — browser-only or against your real app."),
            h.main(".gallery-main")[panels],
            h.script[raw(SCRIPT)],
        ],
    ]
    return str(document)


def build(out: str | Path = "_site", *, theme: Theme = DARK) -> Path:
    """Render the gallery: index, tests, frameworks, ask, and pytest pages."""

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    index = out_dir / "index.html"
    index.write_text(render_gallery(theme), encoding="utf-8")
    (out_dir / "tests.html").write_text(render_tests(theme), encoding="utf-8")
    (out_dir / "frameworks.html").write_text(render_frameworks(theme), encoding="utf-8")
    (out_dir / "ask.html").write_text(render_ask(theme), encoding="utf-8")
    (out_dir / "pytest.html").write_text(render_pytest(theme), encoding="utf-8")
    return index
