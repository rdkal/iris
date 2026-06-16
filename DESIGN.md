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
   a data tree *and* an app shell with stateful, fixi-driven navigation.
6. **Framework-agnostic.** iris produces strings / async chunks. It plugs into
   FastAPI, Starlette, Django, Flask, or a plain WSGI/ASGI app with a one-line
   adapter. iris owns the view layer, never the server.
7. **No build step.** Pure Python in, HTML + one static CSS file out. For
   interactivity, iris uses [fixi](https://github.com/bigskysoftware/fixi)
   (~1.5KB gzipped) plus a small first-party extension — still no bundler.
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

# Lazy-load via fixi, showing a skeleton until the real content swaps in.
lazy_feed = with_loading(feed, skeleton=feed_skeleton, src="/feed")

# Catch render-time exceptions in a subtree and show a fallback instead.
safe_card = error_boundary(article_card, fallback=broken_card)

# Wrap a list renderer with fixi infinite-scroll pagination.
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

Views are **always written explicitly**: a function takes typed data in and
builds the component tree out, using ordinary Python (comprehensions, `if`,
loops). iris never generates a view for you — it only decides *which* explicit
view to call when walking a heterogeneous data tree. There are two ways it
finds that view, and they layer.

**(a) The `__iris__` protocol — duck-typed, used if present.** Just like Python
turns a value into text by calling `__str__`, iris turns a value into a `Node`
by calling `__iris__` if the object defines it. This is the recommended path
for types you own:

```python
from iris import h
from iris.components import card, grid

@dataclass
class Article:
    title: str
    body: str
    def __iris__(self) -> h.Node:          # self-rendering, duck-typed
        return card[h.h2[self.title], h.p[self.body]]

@dataclass
class Gallery:
    items: list[Article]
    def __iris__(self) -> h.Node:
        # explicit tree-building; render() recurses into each child
        return grid(cols=2)[(render(a) for a in self.items)]

render(load_document())   # walks the tree, calling __iris__ on each node
```

`render(x)` resolves a node in this order: it's already an htpy `Node` → use it;
`str`/`None`/`False`/iterables → htpy's own rules; has `__iris__` → call it;
otherwise → registry (below) → error. The walk is just `render` re-entering
itself on children — the recursion is explicit in your comprehensions.

**(b) The Registry — opt-in, for types you don't own or context-specific
views.** When you can't put `__iris__` on a type (third-party/ORM model), or you
want the *same* data to render differently in different places (a compact list
vs. a full page), register the mapping externally instead:

```python
from iris import Registry, h

compact = Registry()

@compact.renders(Article)
def _(a: Article) -> h.Node:
    return h.li[a.title]          # different view of the same Article

compact.render(articles)          # dispatch by type: exact → MRO → fallback
```

A `Registry` is itself callable as a renderer, so a registry and `__iris__`
types compose in the same tree. Both routes ultimately call plain, explicit
view functions — the protocol/registry only choose *which* one.

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
SSR, SEO, JS-free flows.

```python
from iris.app import page

@page("/articles/{slug}")
def article_page(slug: str) -> h.Node:
    a = repo.get(slug)
    return document(title=a.title)[ container[ article_card(a) ] ]
```

### 5.2 App-like navigation (the "app shell")

For app-feel UIs, iris provides `AppShell`: a persistent header + bottom tab bar
(mobile-native pattern) with a fixi-swapped content region. Tabs issue an
`fx-action` request targeting the main region (`fx-target`, `fx-swap`) without a
full reload; the URL updates via iris's fixi history extension (fixi core has no
push-URL — see §7). This gives an SPA feel with zero client framework.

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

# Each tab endpoint returns just the inner fragment for fixi swaps:
@partial("/search")
def search_view() -> h.Node: ...
```

- **Mobile:** bottom tab bar (thumb-reachable), header collapses.
- **Wider:** the same tabs render as a side rail (one media query, no new API).
- **Back/forward & deep links** work because every tab has a real URL.

`partial` vs `page`: a `page` returns a full `<html>` document; a `partial`
returns a fragment intended for fixi swaps. The same view functions are reused
in both.

---

## 6. Higher-order component catalog

| HOC                 | What it does                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `with_loading`      | fixi lazy-load; show `skeleton` until `src` content swaps in       |
| `error_boundary`    | Catch exceptions in a subtree; render `fallback` instead           |
| `paginated`         | fixi infinite-scroll / "load more" over a list renderer            |
| `list_of`           | Map a single-item renderer over an iterable (+ empty state)        |
| `guarded`           | Render only if a predicate over context passes (auth/flags)        |
| `memoized`          | Cache rendered output by a key fn (per-process / pluggable cache)  |
| `responsive`        | Show/hide or swap a subtree by breakpoint (`show_on`, `hide_on`)   |
| `with_skeleton`     | Attach a matching skeleton placeholder to a component              |
| `polling`           | Live refresh via iris's fixi polling extension (`every Ns`)        |
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

### fixi helpers + the iris fixi extension

`iris.integrations.fixi` provides typed wrappers that emit fixi's six
attributes (`fx_action`, `fx_method`, `fx_trigger`, `fx_target`, `fx_swap`). The
`@partial`/`@page` decorators (`iris.app`, §5.2) handle the rest: they detect
fixi's `FX-Request: true` header to return a fragment vs. a full document from
the *same* view function, and set the appropriate `Vary` header.

fixi is intentionally tiny and omits several things iris's navigation/HOCs need.
iris ships one small first-party script, `iris-fixi.js`, that adds them purely
through fixi's event API (`fx:config`, `fx:before`, `fx:swapped`) — no fork:

- **history / push-URL** — update `location` and handle back/forward (powers the
  app shell's deep links).
- **polling** — `every Ns` triggers (powers the `polling` HOC).
- **loading indicators** — toggle a class / swap a skeleton during the request
  (powers `with_loading`).
- **debounce** and **confirm** — convenience hooks on `fx:config`.

`document()` can include both `fixi.js` and `iris-fixi.js` automatically (opt-out
for pure data-driven pages that need no JS).

---

## 8. Component library (initial set)

Built from the primitives + tokens. All dark-first, minimal, accessible.

- **Layout:** container, stack, row, grid, center, sheet, divider, spacer
- **Navigation:** app shell, header, bottom tabs / side rail, breadcrumbs, link
- **Data display:** card, list, table (responsive → stacked rows on mobile),
  key-value, badge/tag, avatar, stat, empty-state
- **Feedback:** skeleton, spinner, toast, banner/alert, progress
- **Forms:** field, input, textarea, select, switch, checkbox, button, form
  (label/error wiring + fixi submit helpers)
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
    fastapi.py  starlette.py  flask.py  django.py  fixi.py
  gallery/
    __init__.py          # gallery registry + @example
    build.py             # static site builder ( -m iris.gallery build )
    theme.py             # gallery chrome (phone frame, code panel)
assets/
  iris.css               # generated reference stylesheet (also producible at runtime)
  fixi.js                # vendored fixi (~1.5KB gzip)
  iris-fixi.js           # first-party fixi extension: history, polling, indicators
docs/                    # built GitHub Pages output (gitignored or committed)
examples/
  fastapi_app/           # end-to-end reference app (data-driven + app shell)
.github/workflows/pages.yml
DESIGN.md
README.md
pyproject.toml
```

---

## 11. Decisions

Resolved:

1. **Min Python: 3.11+** (`Self`, better typing, `tomllib`); matches htpy's
   modern-Python stance.
2. **Interactivity: fixi, not htmx.** fixi is vendored and iris adds the missing
   pieces (history, polling, indicators) via a small first-party extension
   (§7). Data-driven pages still work with zero JS.
3. **Dispatch: explicit views, found via the `__iris__` protocol (duck-typed,
   default) with an opt-in `Registry`** for unowned/context-specific types
   (§2.3). Views are never auto-generated.
4. **Docs: static GitHub Pages**, built from the gallery into a Pages artifact
   on push to `main` (§9).

Still to confirm:

5. **Context for cross-cutting data** (current user, theme, request): lean on
   htpy's `Context` (provider/consumer) so HOCs like `guarded` read context
   without prop-drilling. Confirm this over a custom context.
6. **Icons:** ship a curated inline-SVG set vs. depend on an icon font. Proposed:
   inline SVG (themeable via `currentColor`, no extra request).

---

## 12. Roadmap (suggested order)

1. `core` + `html` (`h`) + `theme` (tokens + `stylesheet`) — the foundation.
2. Layout primitives + the dark stylesheet.
3. `Registry` (data→component mapping) + a couple of data-display components.
4. FastAPI integration (`IrisResponse`) + a minimal example app.
5. HOCs: `list_of`, `with_loading`, `error_boundary`, `paginated`.
6. App shell + navigation (bottom tabs / side rail) + fixi helpers + `iris-fixi.js`.
7. Gallery framework + static build + GitHub Pages workflow.
8. Fill out the component library + forms + overlays.
