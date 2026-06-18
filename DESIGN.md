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

---

## 8. The showcase / docs site (GitHub Pages)

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

## 9. Project layout

```
iris/
  __init__.py            # public API: components, h, component, render, render_stream
  core.py                # @component wrapper, Node helpers, render/render_stream
  html.py                # re-export of htpy + iris extras (h)
  theme.py               # Theme dataclass, tokens, stylesheet() generator
  components/
    layout.py  surfaces.py  nav.py  data.py  forms.py  feedback.py  overlay.py  icons.py
  integrations/
    fastapi.py  starlette.py  flask.py  django.py
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

## 10. Decisions

- **Min Python:** 3.11+.
- **Composition model:** components are htpy-style calls; compose by nesting and
  comprehensions. No registry, no protocol dispatch.
- **Interactivity:** fixi (vendored) + a small first-party `iris-fixi.js`;
  data-driven pages need zero JS.
- **Docs:** static gallery → GitHub Pages on push to `main`.
- **Icons:** curated inline-SVG set, themed via `currentColor`.

## 11. Roadmap (suggested order)

1. `core` (`@component`, `render`) + `html` (`h`) + `theme` (tokens + stylesheet).
2. Layout + surfaces + the dark stylesheet.
3. Navigation (`AppShell`, bottom tabs / side rail) + fixi + `iris-fixi.js`.
4. FastAPI integration + a minimal example app.
5. Gallery framework + static build + GitHub Pages workflow.
6. Fill out data display, forms, feedback, overlay, icons.
```
