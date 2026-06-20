# iris

A small, server-side UI toolkit for Python, built on [htpy](https://htpy.dev).

You build pages by **composing components** — plain function calls that nest just
like htpy, but hand you ready-made UI pieces (`Page`, `Card`, `Grid`, `Stack`, …)
that are dark, minimal, and mobile-first by default.

```python
from iris import Page, Stack, Grid, Card, h, render

doc = Page(title="Today")[
    Stack(gap=3)[
        h.h1["Menu"],
        Grid(cols=2)[
            Card[ h.h3["Eggs"],  h.p["with spam"] ],
            Card[ h.h3["Bacon"], h.p["with eggs"] ],
        ],
    ]
]

html = render(doc)   # a full, self-contained HTML document
```

- `Comp(...)` sets props — htpy class/id shorthand (`".primary"`, `"#main"`),
  keyword attributes, and `fx_*` attributes for [fixi](https://github.com/bigskysoftware/fixi).
- `Comp[...]` sets children — the same bracket syntax as htpy.
- `h` is htpy itself, so raw tags mix freely with components.

Write your own component — it's just a function:

```python
from iris import component, Card, Row, h

@component
def ArticleCard(children, *, title, body, tags):
    return Card[
        h.h2[title],
        h.p[body],
        Row(gap=1)[(h.span(".tag")[t] for t in tags)],
    ]
```

## Component gallery

Every component carries its own usage examples (`@Comp.example`), which double as
live, browsable docs. Build the static gallery (live render + copyable source for
each component) and open it:

```bash
python -m iris.gallery build -o _site
open _site/index.html
```

It deploys to GitHub Pages automatically via `.github/workflows/pages.yml` on
push to `main` (enable Pages → "GitHub Actions" in repo settings).

## Interactivity & testing

Interactive pages use [fixi](https://github.com/bigskysoftware/fixi) (vendored)
plus a small `iris-fixi.js` (history, polling, loading indicators). Render the
host page with `Page(fixi=True)` to inline both. Components emit `fx_*`
attributes (`fx_action`, `fx_target`, `fx_swap`, …); `AppShell`/`Tabs`/`NavLink`
swap a main region without full reloads.

For testing, `iris.testing` has a **stub mode** that runs purely in the browser:
define the view + routes (URL → component tree) + steps as data, and iris builds
a self-contained page that intercepts fixi requests, runs the steps, and reports
pass/fail in-page.

```python
from iris import Button, h
from iris.testing import browser_test, click, expect_text, run_in_browser

test = browser_test(
    view=h.div[h.div("#out")["initial"], Button(fx_action="/next", fx_target="#out")["Load"]],
    routes={"/next": h.p["swapped content"]},
    steps=[click("button"), expect_text("swapped content")],
)
test.write("test.html")            # open in any browser — it runs itself
run_in_browser(test).assert_ok()   # or drive headless Chromium
```

## FastAPI

```python
from fastapi import FastAPI
from iris import Page, Container, h
from iris.integrations.fastapi import IrisResponse

app = FastAPI()

@app.get("/")
def home() -> IrisResponse:                    # streams text/html
    return IrisResponse(Page(title="Home")[Container[h.h1["Hello"]]])
```

`is_fx(request.headers)` lets one view return a full `Page` on a direct visit or
a bare fragment for a fixi swap. See `examples/fastapi_app.py` for an app-shell
app, and the **Frameworks** page of the gallery for more. Install with
`pip install "iris-ui[fastapi]"`.

## Status

Early. See [DESIGN.md](./DESIGN.md) for the full design and [TODO.md](./TODO.md)
for what's built. Implemented so far: the core (`@component`, `render`,
`render_stream`, `is_fx`, `raw`), the theme tokens + dark stylesheet, the layout,
surface, data-display, feedback and navigation components + `Button`, the example
mechanism, the static gallery + Pages workflow, fixi interactivity, and the
stub-mode browser testing harness.

## Install

```bash
pip install -e .          # core
pip install -e ".[test]"  # + pytest & playwright (browser testing, WIP)
```

## License

MIT
