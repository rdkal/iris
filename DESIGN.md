# iris — Design

A small, server-side UI toolkit for Python, built on [htpy](https://htpy.dev).

You build pages by **composing components** — plain function calls that look and
nest just like htpy, but hand you ready-made UI pieces (`Button`, `Card`,
`Grid`, `Stack`, …) that are dark, minimal, and mobile-first by default. Browse
them all, with their source, on the GitHub Pages gallery.

```python
from iris import Page, Stack, Grid, Card, Button, h

Page(title="Today")[
    Stack(gap=3)[
        h.h1["Menu"],
        Grid(cols=2)[
            Card[ h.h3["Eggs"],  h.p["with spam"] ],
            Card[ h.h3["Bacon"], h.p["with eggs"] ],
        ],
        Button(".primary", fx_action="/order")["Order"],
    ]
]
```

---

## 1. Principles

1. **Thin over htpy.** Every component returns an htpy `Node`. Drop to raw htpy
   any time and back — they mix freely.
2. **Compose by nesting.** The only mental model is "call components, nest them
   with `[...]`, loop with comprehensions." No registries, no dispatch, no magic.
3. **Mobile first, dark, minimal.** Sensible defaults for a phone screen and a
   calm dark theme; you rarely pass style props.
4. **Few CSS variables.** ~12 custom properties drive the whole look; everything
   else is derived. Re-theme by overriding a handful.
5. **Framework-agnostic.** Components render to a string or async stream; FastAPI
   / Flask / Django adapters are one-liners. iris owns the view, never the server.
6. **No build step.** Pure Python in, HTML + one CSS file out. Optional
   interactivity via [fixi](https://github.com/bigskysoftware/fixi) (~1.5KB).
7. **Typed.** Components take typed props; the tree checks with mypy/pyright.

---

## 2. Components are htpy calls

A component is called exactly like an htpy element:

- `Comp(...)` sets **props** — htpy's class/id shorthand (`".primary"`,
  `"#main"`), keyword attributes, and `fx_*` attributes for fixi.
- `Comp[...]` sets **children** — the same bracket syntax as htpy, so strings,
  nodes, lists, generators, and conditionals all work.

```python
from iris import Stack, Card, Button, h

Stack(gap=2)[
    Card[ h.h2["Title"], h.p["Body"] ],
    Button(".primary", disabled=False)["Save"],
    Button(".ghost", fx_action="/cancel", fx_swap="outerHTML")["Cancel"],
]
```

`h` is iris's re-export of htpy, so raw tags (`h.div`, `h.span`) sit right next
to components.

### Writing your own component

It's just a function that returns a node — compose the built-ins:

```python
from iris import component, Card, Row, Tag, h

@component
def ArticleCard(title: str, body: str, tags: list[str]) -> h.Node:
    return Card[
        h.h2[title],
        h.p[body],
        Row(gap=1)[(Tag[t] for t in tags)],
    ]

ArticleCard(title="Hello", body="…", tags=["py", "ui"])
```

The `@component` decorator is a thin wrapper that gives your function the same
htpy-style `(...)`/`[...]` calling convention as the built-ins (and merges
class/`fx_*` props passed at the call site). A component that takes content uses
the `[...]` slot; one that's fully described by props just takes `(...)`.

### Rendering a collection is a comprehension

No special list API — explicit Python:

```python
Stack[ (ArticleCard(title=a.title, body=a.body, tags=a.tags) for a in articles) ]
```

If your data is a tree, you write the recursion yourself with normal function
calls — a `Section` component that maps over its children, etc. That's the whole
"data tree → component tree" story: ordinary functions and comprehensions.

---

## 3. Component set (initial)

All dark-first, minimal, accessible, mobile-first. Each takes typed props and
the htpy `[...]` slot where it holds content.

- **Layout:** `Page`, `Container`, `Stack`, `Row`, `Grid`, `Center`, `Divider`,
  `Spacer`
- **Surfaces:** `Card`, `Sheet`, `Panel`
- **Navigation:** `AppShell`, `Header`, `Tabs`, `NavLink`, `Breadcrumbs`
- **Data display:** `List`, `Table` (stacks into rows on mobile), `Badge`,
  `Tag`, `Avatar`, `Stat`, `Empty`
- **Forms:** `Form`, `Field`, `Input`, `Textarea`, `Select`, `Switch`,
  `Checkbox`, `Button`
- **Feedback:** `Skeleton`, `Spinner`, `Toast`, `Banner`, `Progress`
- **Overlay:** `Drawer` (bottom-sheet on mobile), `Modal`, `Menu`, `Popover`
- **Icons:** a small inline-SVG set (stroke icons, themed via `currentColor`)

---

## 4. Theme: few CSS variables

The whole design system is a small set of custom properties on `:root`. Dark is
the default; light is the same variables with different values.

```css
:root {
  /* color — 6 vars */
  --bg:      #0b0c0e;   /* page background             */
  --surface: #15171b;   /* cards, sheets, nav          */
  --text:    #e7e9ec;   /* primary text                */
  --muted:   #8b9099;   /* secondary text, icons       */
  --accent:  #6ea8fe;   /* the single brand/action hue */
  --border:  #262a31;   /* hairlines, dividers         */

  /* shape & rhythm — 4 vars */
  --space:   0.5rem;    /* base spacing unit (scale = multiples) */
  --radius:  0.75rem;   /* corner rounding             */
  --font:    system-ui, sans-serif;
  --measure: 38rem;     /* max readable line / container width */
}
```

Everything else is **derived** from these, so the knob count stays tiny:

```css
.stack > * + * { margin-top: calc(var(--space) * var(--gap, 2)); }
.elevated      { background: color-mix(in oklab, var(--surface), white 4%); }
.btn:hover     { background: color-mix(in oklab, var(--accent), white 12%); }
```

Re-theming overrides a few variables — no recompile:

```python
from iris.theme import Theme
brand = Theme(accent="#22d3aa", radius="0.25rem")   # sharper, teal
```

Light mode is one extra block toggled by `prefers-color-scheme` and/or a
`data-theme="light"` attribute, so a user-facing toggle is a single attribute
flip. iris ships one static, cacheable stylesheet, `iris.css`, generated from
the tokens; component classes (`.stack`, `.grid`, `.card`, …) are hand-written,
not atomic utilities — the file is small enough to read in a sitting.

---

## 5. Mobile-first layout & navigation

Layout primitives assume a phone first and widen with one `--measure`-based
media query — base styles need no media query at all. `Grid(cols=2)` is two
columns on a tablet and one on a phone; `Row` wraps.

iris covers both page styles, using the same components:

- **Data-driven pages** — a view is a function returning a `Page`. Great for
  content, SSR, SEO; works with zero JS.

  ```python
  def article_page(slug: str) -> h.Node:
      a = repo.get(slug)
      return Page(title=a.title)[ Container[ ArticleCard(a.title, a.body, a.tags) ] ]
  ```

- **App-like shell** — `AppShell` gives a persistent header + bottom tab bar
  (thumb-reachable; becomes a side rail on wide screens via one media query).
  Tabs swap the content region with fixi instead of full reloads, with real URLs
  so back/forward and deep links work.

  ```python
  AppShell(title="iris", tabs=[
      Tab("Home", icon="home", src="/home"),
      Tab("Search", icon="search", src="/search"),
      Tab("Profile", icon="user", src="/me"),
  ])[ home_view() ]
  ```

---

## 6. Interactivity: fixi (optional)

For app-like behavior, components emit [fixi](https://github.com/bigskysoftware/fixi)
attributes via `fx_*` kwargs (`fx_action`, `fx_method`, `fx_target`, `fx_swap`,
`fx_trigger`). fixi is ~1.5KB and deliberately omits history, polling, and
loading indicators — so iris ships a tiny first-party `iris-fixi.js` that adds
exactly those through fixi's event API (`fx:config`, `fx:before`, `fx:swapped`).
`Page`/`AppShell` can include both scripts automatically (opt-out for pure
data-driven pages).

iris detects fixi's `FX-Request: true` header so the *same* view function can
return a full `Page` for a normal request and just the inner fragment for a
fixi swap.

### Forms round-trip

A `Form` posts via fixi (`fx_action`, `fx_method="post"`) and targets a region to
swap. The server validates and re-renders: on success, swap in the next view; on
failure, re-render the *same* `Form` with errors. `Field` has an error slot, so
the view function is the single source of truth for both the empty and the error
state — no separate error template.

```python
def signup_form(values=None, errors=None) -> h.Node:
    values, errors = values or {}, errors or {}
    return Form(fx_action="/signup", fx_method="post", fx_target="#signup")[
        Field(label="Email", error=errors.get("email"))[
            Input(name="email", value=values.get("email", "")),
        ],
        Button(".primary")["Create account"],
    ]

@app.post("/signup")                       # framework route; returns a fragment
def signup(request):
    data = parse(request)
    if errors := validate(data):
        return IrisResponse(signup_form(values=data, errors=errors), status=422)
    create_user(data)
    return IrisResponse(welcome_view())
```

---

## 7. Framework integration

Components produce a `Node`; adapters turn it into a response. Streaming uses
htpy's `iter_chunks()` for low time-to-first-byte.

```python
# FastAPI / Starlette — streams text/html
from iris.integrations.fastapi import IrisResponse

@app.get("/")
def home() -> IrisResponse:
    return IrisResponse(article_page("hello"))

# Anything else
from iris import render          # -> str
from iris import render_stream   # -> Iterator[str] / AsyncIterator[str]

@app.get("/")
def home(): return render(article_page("hello"))   # Flask / Django / WSGI
```

### Routing (iris does none)

iris never owns URLs — your web framework does. A view is just a function
returning a `Node`, wired to a route with your framework's normal decorator. The
only iris touch-point is choosing whether to return a full `Page` or a bare
fragment for a fixi swap, via a one-line header check:

```python
from iris import is_fx                       # is_fx(headers: Mapping[str, str]) -> bool
from iris.integrations.fastapi import IrisResponse

@app.get("/home")                            # FastAPI owns the route
def home(request):
    content = home_view()                    # same content either way
    if is_fx(request.headers):               # fixi swap → fragment only
        return IrisResponse(content)
    return IrisResponse(shell[content])      # normal request → full Page/shell
```

`AppShell` tabs and `fx_action` targets just reference these framework URLs as
strings; iris emits the attributes, your framework resolves the routes. `is_fx`
takes any header mapping, so it works the same in Flask, Django, or plain
ASGI/WSGI.

---

## 8. Testing

UI tests are usually flaky because they assert on *appearance*. iris ships only
the tests with the opposite property — binary, **"did it crash"** checks — and it
does so as a thin **convenience over Playwright, not an abstraction**. You keep
the real Playwright `Page`, locators, and `expect`; iris only makes it easy to
(a) get an iris page into the browser and (b) assert that nothing threw or
returned a bad status code.

### What iris adds (and what it deliberately doesn't)

iris adds exactly two things:

1. **An error collector** — attach it to any Playwright page; it records uncaught
   JS exceptions, `console.error`, fixi `fx:error` events, and HTTP responses
   with disallowed status codes, then fails the test with the real JS stack
   trace. Because iris installs the fixi hook via `page.add_init_script`, it runs
   *before* fixi and your code, so nothing is missed.
2. **Two ways to load a page** — an isolated rendered node, or your real running
   app.

iris does **not** wrap clicking, filling, navigation, waiting, or assertions —
that stays plain Playwright. No `page.click()` reinvention, no locator DSL.

### Error collector

```python
from iris.testing import collect_errors

def test_home(page):                      # real pytest-playwright `page` fixture
    errors = collect_errors(page)         # hooks pageerror, console.error, fx:error, responses
    page.goto(url)
    errors.assert_none()                  # fails with the JS stack trace if anything threw
```

Under the hood it's just Playwright events — `page.on("pageerror")`,
`page.on("console")`, `page.on("response")` — plus one init script that forwards
fixi's `fx:error`. Which status codes count as failures is configurable:

```python
errors = collect_errors(page, fail_on_status=range(400, 600))   # default
errors.responses          # every observed response, to inspect if you want
```

### Mode A — isolated page (smoke-test a render)

Serve a single rendered node (with `iris.css` + `fixi.js` + `iris-fixi.js`) on a
throwaway URL — good for "this page boots and fixi initializes without error."

```python
from iris.testing import serve

def test_card_boots(page):
    errors = collect_errors(page)
    with serve(article_page("hello")) as url:
        page.goto(url)
    errors.assert_none()
```

### Mode B — your real app (exercise fixi swaps end-to-end)

Run the user's ASGI/WSGI app on a real port so `fx_action` swaps hit real routes,
then drive it with ordinary Playwright:

```python
from iris.testing import live_app
from playwright.sync_api import expect
from myapp import app

def test_order_flow(page):
    errors = collect_errors(page)
    with live_app(app) as base_url:
        page.goto(base_url)
        page.get_by_role("button", name="Order").click()    # plain Playwright
        expect(page.get_by_text("Order placed")).to_be_visible()
    errors.assert_none()                                     # ...and nothing threw / no 5xx
```

`serve`, `live_app`, and `collect_errors` are also exposed as pytest fixtures to
skip the boilerplate.

### No-browser checks come free

Components are pure `data → HTML` functions, so the cheapest tests need no iris
test API at all — call `render()` and assert on the string with plain Python:

```python
from iris import render, Button
def test_button_has_action():
    assert 'fx-action="/order"' in render(Button(fx_action="/order")["Order"])
```

iris ships no DSL for this — it's just a function returning a string.

Playwright is an optional extra: `pip install iris[test]`.

---

## 9. The showcase / docs site (GitHub Pages)

A live gallery where every component is shown **rendered** next to the **exact
Python that produced it** — the fastest way to start.

- A `@gallery.example` decorator registers an example. iris captures the source
  with `inspect.getsource`, renders the component, and pairs them.

  ```python
  from iris.gallery import gallery
  from iris import Row, Button

  @gallery.example("Buttons", "Primary & ghost")
  def buttons():
      return Row(gap=2)[ Button(".primary")["Save"], Button(".ghost")["Cancel"] ]
  ```

- Each example renders as a panel: a phone-frame live preview, a
  syntax-highlighted, copy-able code block, and a light/dark toggle. The gallery
  is built *with* iris (dogfooding).
- A build command renders the gallery to static HTML
  (`python -m iris.gallery build -o _site`); a GitHub Action publishes it to
  GitHub Pages on push to `main`. No server needed for the docs.

```yaml
# .github/workflows/pages.yml
name: Deploy gallery
on: { push: { branches: [main] } }
permissions: { pages: write, id-token: write, contents: read }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e .
      - run: python -m iris.gallery build -o _site
      - uses: actions/upload-pages-artifact@v3
        with: { path: _site }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages }
    steps: [ { uses: actions/deploy-pages@v4 } ]
```

---

## 10. Project layout

```
iris/
  __init__.py            # public API: components, h, component, render, render_stream, is_fx
  core.py                # @component wrapper, Node helpers, render/render_stream, is_fx
  html.py                # re-export of htpy + iris extras (h)
  theme.py               # Theme dataclass, tokens, stylesheet() generator
  components/
    layout.py  surfaces.py  nav.py  data.py  forms.py  feedback.py  overlay.py  icons.py
  integrations/
    fastapi.py  starlette.py  flask.py  django.py
  testing.py             # collect_errors, serve, live_app + pytest fixtures (extra: iris[test])
  gallery/
    __init__.py          # gallery registry + @example
    build.py             # static site builder ( -m iris.gallery build )
assets/
  iris.css   fixi.js   iris-fixi.js
examples/
  fastapi_app/           # reference app (data-driven page + app shell)
.github/workflows/pages.yml
DESIGN.md  README.md  pyproject.toml
```

---

## 11. Decisions

- **Min Python:** 3.11+.
- **Composition model:** components are htpy-style calls; compose by nesting and
  comprehensions. No registry, no protocol dispatch.
- **Interactivity:** fixi (vendored) + a small first-party `iris-fixi.js`;
  data-driven pages need zero JS.
- **Docs:** static gallery → GitHub Pages on push to `main`.
- **Icons:** curated inline-SVG set, themed via `currentColor`.
- **Testing:** convenience over Playwright (never an abstraction) — `collect_errors`
  (JS exceptions, `console.error`, fixi `fx:error`, bad status codes) plus
  `serve` (isolated) and `live_app` (real app) loaders. Optional extra `iris[test]`.

## 12. Roadmap (suggested order)

1. `core` (`@component`, `render`) + `html` (`h`) + `theme` (tokens + stylesheet).
2. Layout + surfaces + the dark stylesheet.
3. Navigation (`AppShell`, bottom tabs / side rail) + fixi + `iris-fixi.js`.
4. FastAPI integration + a minimal example app.
5. Testing harness (`iris.testing`): `collect_errors` + `serve`/`live_app` + fixtures.
6. Gallery framework + static build + GitHub Pages workflow.
7. Fill out data display, forms, feedback, overlay, icons.
```
