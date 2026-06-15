# iris — Design

A small, server-side UI library for Python, built on [htpy](https://htpy.dev).

> You have data. Data is a tree. iris maps that tree to a tree of
> **components**, which htpy renders to a tree of **HTML**. No build step, no
> JavaScript framework, no template language — just Python functions.

```
your data (tree)  ──▶  components (tree)  ──▶  htpy nodes  ──▶  HTML (tree)
```

---

## 1. Goals & principles

1. **Thin over htpy.** iris never hides htpy. Everything iris returns *is* an
   htpy `Node`, so users can always drop down to raw htpy and back. We add
   composition, a design system, and conventions — not a wall.
2. **Mobile first.** Every primitive is designed for a narrow viewport first
   and enhances upward. Touch targets, bottom navigation, single-column stacks
   are the defaults.
3. **Dark, minimal, calm.** The default theme is dark. The visual language is
   flat, high-contrast-where-it-matters, generous whitespace, one accent color.
4. **Few CSS variables.** The entire look is driven by ~12 CSS custom
   properties. Everything else is *derived* from them. Re-theming = override a
   handful of variables.
5. **Data-driven *and* app-like.** The same library renders a content page from
   a data tree *and* an app shell with stateful, htmx-driven navigation.
6. **Framework-agnostic.** iris produces strings / async chunks. It plugs into
   FastAPI, Starlette, Django, Flask, or a plain WSGI/ASGI app with a one-line
   adapter. iris owns the view layer, never the server.
7. **No build step.** Pure Python in, HTML + one static CSS file out. Optionally
   sprinkle [htmx](https://htmx.org) for interactivity — still no bundler.
8. **Typed.** Components take typed props (dataclasses / `TypedDict`). The tree
   is checkable with mypy/pyright.

---

## 2. Mental model

### 2.1 Components

A **component** is a plain function from props to an htpy `Node`:

```python
from dataclasses import dataclass
from iris import h
from iris.components import card, stack

@dataclass
class Article:
    title: str
    body: str
    tags: list[str]

def article_card(a: Article) -> h.Node:
    return card[
        h.h2[a.title],
        h.p[a.body],
        stack(direction="row", gap=1)[(h.span(".tag")[t] for t in a.tags)],
    ]
```

`h` is iris's re-export of htpy plus a few extra elements/helpers, so users
import from one place: `from iris import h`.

Components are just functions, so all of Python composes them: loops,
comprehensions, conditionals, decorators, modules.

### 2.2 Higher-order components (HOCs)

A **higher-order component** takes a component (or props) and returns a
component, adding behavior without touching the original. This is the headline
feature.

```python
from iris.hoc import with_loading, error_boundary, paginated, guarded

# Lazy-load via htmx, showing a skeleton until the real content swaps in.
lazy_feed = with_loading(feed, skeleton=feed_skeleton, src="/feed")

# Catch render-time exceptions in a subtree and show a fallback instead.
safe_card = error_boundary(article_card, fallback=broken_card)

# Wrap a list renderer with htmx infinite-scroll pagination.
feed = paginated(article_card, page_size=20, src="/feed")

# Render only if a predicate passes (auth / feature flag), else nothing.
admin_panel = guarded(panel, when=lambda ctx: ctx.user.is_admin)
```

HOCs compose like decorators:

```python
feed = with_loading(error_boundary(paginated(article_card)))
```

See §6 for the full HOC catalog.

### 2.3 The data → component mapping (the core idea)

When data is a heterogeneous tree (a CMS document, a JSON API payload, a
notebook of blocks), you don't want a giant `if/elif` on node type. iris
provides a **Registry**: register one renderer per data type, then ask iris to
render the whole tree. iris walks the data, dispatches each node to its
renderer by type, and recurses into children automatically.

```python
from iris import Registry, h

ui = Registry()

@ui.renders(Heading)
def _(n: Heading) -> h.Node:
    return h.h2[n.text]

@ui.renders(Paragraph)
def _(n: Paragraph) -> h.Node:
    return h.p[n.text]

@ui.renders(Gallery)
def _(n: Gallery) -> h.Node:
    # children are rendered by re-entering the registry — this is the recursion
    return grid(cols=2)[ui.render_each(n.items)]

# One call turns an arbitrary data tree into HTML.
document: list[Block] = load_document()
html = ui.render(document)
```

Dispatch rules, in order: exact type → registered base class (MRO walk) →
a fallback renderer (`@ui.fallback`) → error. This keeps the mapping declarative
and open for extension: add a node type, add a renderer, done.

> **Why a registry instead of methods on the data?** It keeps your data classes
> free of presentation, lets the same data render differently in different
> contexts (e.g. a compact registry vs. a full registry), and makes the
> data→view boundary explicit.

---

## 3. Theming: few CSS variables

The whole design system is a small set of custom properties on `:root`.
Dark is the default; light is the same variables with different values.

```css
:root {
  /* color — 6 vars */
  --bg:      #0b0c0e;   /* page background            */
  --surface: #15171b;   /* cards, sheets, nav          */
  --text:    #e7e9ec;   /* primary text                */
  --muted:   #8b9099;   /* secondary text, icons       */
  --accent:  #6ea8fe;   /* the single brand/action hue */
  --border:  #262a31;   /* hairlines, dividers         */

  /* shape & rhythm — 4 vars */
  --space:   0.5rem;    /* base spacing unit (scale = multiples) */
  --radius:  0.75rem;   /* corner rounding              */
  --font:    system-ui, sans-serif;
  --measure: 38rem;     /* max readable line / container width */
}
```

Everything else is **derived** in CSS from these, so the knob count stays tiny:

```css
/* spacing scale = multiples of --space (no new variables) */
.stack > * + * { margin-top: calc(var(--space) * var(--gap, 2)); }

/* "elevated" surfaces nudge lightness without a new color var */
.elevated { background: color-mix(in oklab, var(--surface), white 4%); }

/* hover/active states derive from --accent */
.btn:hover { background: color-mix(in oklab, var(--accent), white 12%); }
```

**Re-theming** is overriding a few variables — no recompile, no rebuild:

```python
from iris.theme import Theme

brand = Theme(accent="#22d3aa", radius="0.25rem")   # sharper, teal
# emits :root { --accent:#22d3aa; --radius:0.25rem }  (only the diffs)
```

Light mode ships as one extra block toggled by `prefers-color-scheme` and/or a
`data-theme` attribute, so a user-facing toggle is a single attribute flip:

```css
[data-theme="light"] {
  --bg:#ffffff; --surface:#f5f6f8; --text:#13151a;
  --muted:#5b6470; --border:#e3e6ea;
}
```

### CSS delivery

One static stylesheet, `iris.css`, generated from the tokens at build/startup —
no per-request inlining, fully cacheable. Layout primitives use a fixed,
hand-written set of utility classes (`.stack`, `.row`, `.grid`, `.container`,
`.card`, …); we deliberately **do not** ship a Tailwind-style atomic framework.
The CSS file is small enough to read in one sitting, which is the point.

```python
from iris.theme import stylesheet
app.mount("/static/iris.css", stylesheet(brand))   # or write it to disk once
```

---

## 4. Layout primitives (mobile-first)

A handful of composable primitives, each a thin div + utility class. Defaults
assume a phone; props widen behavior at breakpoints.

| Primitive            | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `container`          | Centered column capped at `--measure`            |
| `stack`              | Vertical flow with consistent gap (the default)  |
| `row`                | Horizontal flex; wraps on small screens          |
| `grid(cols=…)`       | Responsive grid; collapses to 1 col on mobile    |
| `center`             | Centers child both axes                          |
| `spacer` / `divider` | Flexible gap / hairline                          |
| `sheet`              | Surface card (`--surface`, `--radius`, padding)  |

```python
container[
    stack(gap=3)[
        h.h1["Today"],
        grid(cols=2)[(article_card(a) for a in articles)],  # 1 col on phones
    ]
]
```

Breakpoints are derived, not configurable per-call: one `--measure`-based
media query. Mobile-first means the base styles need no media query at all.

---

## 5. Navigation: data-driven pages *and* app-like shell

iris supports two modes that share the same components.

### 5.1 Data-driven pages

A page is a function from request/data to a full document. Good for content,
SSR, SEO, htmx-free flows.

```python
from iris.app import page

@page("/articles/{slug}")
def article_page(slug: str) -> h.Node:
    a = repo.get(slug)
    return document(title=a.title)[ container[ article_card(a) ] ]
```

### 5.2 App-like navigation (the "app shell")

For app-feel UIs, iris provides `AppShell`: a persistent header + bottom tab bar
(mobile-native pattern) with an htmx-swapped content region. Tabs swap the main
region without a full reload; the URL updates via `hx-push-url`. This gives an
SPA feel with zero client framework.

```python
from iris.app import AppShell, Tab

shell = AppShell(
    title="iris",
    tabs=[
        Tab("Home",    icon="home",     src="/home"),
        Tab("Search",  icon="search",   src="/search"),
        Tab("Profile", icon="user",     src="/me"),
    ],
)

@page("/")
def root() -> h.Node:
    return shell.render(active="Home", content=home_view())

# Each tab endpoint returns just the inner fragment for htmx swaps:
@partial("/search")
def search_view() -> h.Node: ...
```

- **Mobile:** bottom tab bar (thumb-reachable), header collapses.
- **Wider:** the same tabs render as a side rail (one media query, no new API).
- **Back/forward & deep links** work because every tab has a real URL.

`partial` vs `page`: a `page` returns a full `<html>` document; a `partial`
returns a fragment intended for htmx swaps. The same view functions are reused
in both.

---

## 6. Higher-order component catalog

| HOC                 | What it does                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `with_loading`      | htmx lazy-load; show `skeleton` until `src` content swaps in       |
| `error_boundary`    | Catch exceptions in a subtree; render `fallback` instead           |
| `paginated`         | htmx infinite-scroll / "load more" over a list renderer            |
| `list_of`           | Map a single-item renderer over an iterable (+ empty state)        |
| `guarded`           | Render only if a predicate over context passes (auth/flags)        |
| `memoized`          | Cache rendered output by a key fn (per-process / pluggable cache)  |
| `responsive`        | Show/hide or swap a subtree by breakpoint (`show_on`, `hide_on`)   |
| `with_skeleton`     | Attach a matching skeleton placeholder to a component              |
| `polling`           | htmx `hx-trigger="every Ns"` live refresh                          |
| `with_a11y`         | Inject ARIA roles/labels and ensure focus order for a subtree      |

All HOCs share one signature shape so they compose cleanly:

```python
Component = Callable[P, h.Node]
HOC       = Callable[[Component], Component]   # plus config via closure/partial
```

---

## 7. Framework integration

iris produces a `Node`; adapters turn it into a framework response. Streaming
uses htpy's `iter_chunks()` for low time-to-first-byte.

### FastAPI / Starlette (async + streaming)

```python
from fastapi import FastAPI
from iris.integrations.fastapi import IrisResponse

app = FastAPI()

@app.get("/")
def home() -> IrisResponse:
    return IrisResponse(document(title="Home")[container[home_view()]])
    # IrisResponse streams node.iter_chunks() with text/html
```

### Anything else

```python
from iris import render            # -> str
from iris import render_stream      # -> Iterator[str] / AsyncIterator[str]

# Flask
@app.get("/")
def home(): return render(home_view())

# Django
def home(request): return HttpResponse(render(home_view()))
```

### htmx helpers

`iris.integrations.htmx` provides typed wrappers (`hx_get`, `hx_swap`,
`trigger`, `push_url`) and an `hx_partial` decorator that returns a fragment
plus the right `Vary`/`HX-*` headers. iris detects the `HX-Request` header to
return a fragment vs. a full document from the *same* view function.

---

## 8. Component library (initial set)

Built from the primitives + tokens. All dark-first, minimal, accessible.

- **Layout:** container, stack, row, grid, center, sheet, divider, spacer
- **Navigation:** app shell, header, bottom tabs / side rail, breadcrumbs, link
- **Data display:** card, list, table (responsive → stacked rows on mobile),
  key-value, badge/tag, avatar, stat, empty-state
- **Feedback:** skeleton, spinner, toast, banner/alert, progress
- **Forms:** field, input, textarea, select, switch, checkbox, button, form
  (label/error wiring + htmx submit helpers)
- **Overlay:** sheet/drawer (bottom-sheet on mobile), modal, popover, menu
- **Icons:** a small inline-SVG set (stroke icons, themed via `currentColor`)

Each ships with a typed props dataclass and a skeleton variant where it makes
sense (so `with_loading`/`with_skeleton` work out of the box).

---

## 9. The showcase / docs site (GitHub Pages)

A live gallery where every component is shown **rendered** next to the **exact
Python that produced it** — the fastest way for newcomers to start.

### How it works

- A `@gallery.example` decorator registers a component example. iris captures
  the source with `inspect.getsource`, renders the component, and pairs them.

```python
from iris.gallery import gallery

@gallery.example("Buttons", "Primary & ghost")
def buttons() -> h.Node:
    return row(gap=2)[
        button(".primary")["Save"],
        button(".ghost")["Cancel"],
    ]
```

- Each example renders as a **panel**: a phone-frame live preview on top, a
  syntax-highlighted, copy-able code block below, plus a light/dark toggle and a
  "open in new tab" link. This dogfoods iris — the gallery is built *with* iris.
- The gallery is rendered to **static HTML** by a build script
  (`python -m iris.gallery build -o docs/`) and published to GitHub Pages. No
  server needed for the docs; everything is pre-rendered.

### Deployment

`.github/workflows/pages.yml` builds the static gallery into `docs/` (or an
artifact) on every push to the main branch and deploys to GitHub Pages:

```yaml
name: Deploy gallery
on:
  push: { branches: [main] }
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

The same gallery can also be served live (FastAPI route) during development for
hot-reload via the dev server.

---

## 10. Project layout

```
iris/
  __init__.py            # public API: h, render, render_stream, Registry, document
  core.py                # Component/Node types, Registry, render, context glue
  html.py                # re-export of htpy + iris-specific elements/helpers (h)
  theme.py               # Theme dataclass, tokens, stylesheet() generator
  hoc.py                 # higher-order components (§6)
  app.py                 # page/partial decorators, AppShell, Tab, document()
  components/
    layout.py  nav.py  data.py  feedback.py  forms.py  overlay.py  icons.py
  integrations/
    fastapi.py  starlette.py  flask.py  django.py  htmx.py
  gallery/
    __init__.py          # gallery registry + @example
    build.py             # static site builder ( -m iris.gallery build )
    theme.py             # gallery chrome (phone frame, code panel)
assets/
  iris.css               # generated reference stylesheet (also producible at runtime)
docs/                    # built GitHub Pages output (gitignored or committed)
examples/
  fastapi_app/           # end-to-end reference app (data-driven + app shell)
.github/workflows/pages.yml
DESIGN.md
README.md
pyproject.toml
```

---

## 11. Open questions / decisions to confirm

1. **Name & package.** Repo is `iris`; assuming the import name is `iris`.
2. **Min Python.** Proposed **3.11+** (for `Self`, better typing, `tomllib`).
   htpy targets modern Python anyway.
3. **htmx as a hard dependency?** Proposed: htmx is **optional** — data-driven
   pages work with zero JS; the app-shell / HOCs that need interactivity emit
   htmx attributes and document that you must include the htmx script.
4. **Context for cross-cutting data** (current user, theme, request): lean on
   htpy's `Context` (provider/consumer) so HOCs like `guarded` read context
   without prop-drilling. Confirm this over a custom context.
5. **Icons:** ship a curated inline-SVG set vs. depend on an icon font. Proposed:
   inline SVG (themeable via `currentColor`, no extra request).
6. **Docs hosting:** GitHub Pages from `docs/` artifact (above). Confirm branch
   strategy (`main` → Pages).

---

## 12. Roadmap (suggested order)

1. `core` + `html` (`h`) + `theme` (tokens + `stylesheet`) — the foundation.
2. Layout primitives + the dark stylesheet.
3. `Registry` (data→component mapping) + a couple of data-display components.
4. FastAPI integration (`IrisResponse`) + a minimal example app.
5. HOCs: `list_of`, `with_loading`, `error_boundary`, `paginated`.
6. App shell + navigation (bottom tabs / side rail) + htmx helpers.
7. Gallery framework + static build + GitHub Pages workflow.
8. Fill out the component library + forms + overlays.
