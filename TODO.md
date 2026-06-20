# iris — TODO

Status of every piece in [DESIGN.md](./DESIGN.md). Everything is **Designed**.
Built so far: core, theme + dark stylesheet, layout/surface/data/feedback/nav
components + `Button`, the component **example mechanism**, the **gallery** (+
tests & frameworks pages) + Pages, **fixi** (`fixi.js` + `iris-fixi.js`,
`Page(fixi=True)`), **FastAPI integration** (`IrisResponse`), and **both browser
testing modes** (`browser_test`/`run_in_browser`, `collect_errors`, `live_app`)
— all with tests (incl. real-browser and live-app tests).

Legend: ✅ done · ⬜ not started

## Core

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `@component` wrapper (htpy-style `(...)` / `[...]` calling) | ✅ | ✅ | ✅ |
| `render()` → str | ✅ | ✅ | ✅ |
| `render_stream()` → chunk iterator (sync; async pending) | ✅ | ✅ | ✅ |
| `h` — htpy re-export + iris extras | ✅ | ✅ | ✅ |

## Theme

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Theme` dataclass + token set (~12 vars) | ✅ | ✅ | ✅ |
| `stylesheet()` generator | ✅ | ✅ | ✅ |
| Dark default `iris.css` (hand-written component classes) | ✅ | ✅ | ✅ |
| Light mode override (`data-theme`) | ✅ | ✅ | ✅ |

## Components — Layout

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Page` | ✅ | ✅ | ✅ |
| `Container` | ✅ | ✅ | ✅ |
| `Stack` | ✅ | ✅ | ✅ |
| `Row` | ✅ | ✅ | ✅ |
| `Grid` | ✅ | ✅ | ✅ |
| `Center` | ✅ | ✅ | ✅ |
| `Divider` | ✅ | ✅ | ✅ |
| `Spacer` | ✅ | ✅ | ✅ |

## Components — Surfaces

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Card` | ✅ | ✅ | ✅ |
| `Sheet` | ✅ | ✅ | ✅ |
| `Panel` | ✅ | ✅ | ✅ |

## Components — Navigation

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `AppShell` (bottom tabs → side rail) | ✅ | ✅ | ✅ |
| `Header` | ✅ | ✅ | ✅ |
| `Tabs` / `Tab` | ✅ | ✅ | ✅ |
| `NavLink` | ✅ | ✅ | ✅ |
| `Breadcrumbs` | ✅ | ✅ | ✅ |

## Components — Data display

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `List` | ✅ | ✅ | ✅ |
| `Table` | ✅ | ✅ | ✅ |
| `Badge` | ✅ | ✅ | ✅ |
| `Tag` | ✅ | ✅ | ✅ |
| `Avatar` | ✅ | ✅ | ✅ |
| `Stat` | ✅ | ✅ | ✅ |
| `Empty` | ✅ | ✅ | ✅ |

## Components — Forms

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Form` | ✅ | ⬜ | ⬜ |
| `Field` | ✅ | ⬜ | ⬜ |
| `Input` | ✅ | ⬜ | ⬜ |
| `Textarea` | ✅ | ⬜ | ⬜ |
| `Select` | ✅ | ⬜ | ⬜ |
| `Switch` | ✅ | ⬜ | ⬜ |
| `Checkbox` | ✅ | ⬜ | ⬜ |
| `Button` | ✅ | ✅ | ✅ |

## Components — Feedback

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Skeleton` | ✅ | ✅ | ✅ |
| `Spinner` | ✅ | ✅ | ✅ |
| `Toast` | ✅ | ⬜ | ⬜ |
| `Banner` | ✅ | ✅ | ✅ |
| `Progress` | ✅ | ✅ | ✅ |

## Components — Overlay

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `Drawer` (bottom-sheet on mobile) | ✅ | ⬜ | ⬜ |
| `Modal` | ✅ | ⬜ | ⬜ |
| `Menu` | ✅ | ⬜ | ⬜ |
| `Popover` | ✅ | ⬜ | ⬜ |

## Components — Icons

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| Inline-SVG icon set (`currentColor`) | ✅ | ⬜ | ⬜ |

## Interactivity (fixi)

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `fx_*` attribute support on components | ✅ | ✅ | ✅ |
| Vendored `fixi.js` + `Page(fixi=True)` inlining | ✅ | ✅ | ✅ |
| `iris-fixi.js` (history, polling, indicators) | ✅ | ✅ | ⬜ |
| `is_fx()` header check (fragment vs full `Page`) | ✅ | ✅ | ✅ |

## Framework integration

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `IrisResponse` (FastAPI / Starlette, streaming) | ✅ | ✅ | ✅ |
| FastAPI reference app (`examples/fastapi_app.py`) | ✅ | ✅ | ✅ |
| Flask / Django / WSGI `render()` adapters | ✅ | ⬜ | ⬜ |

## Testing (`iris.testing`)

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| Stub mode: `browser_test` + steps + `iris-test.js` (fx:config interceptor) | ✅ | ✅ | ✅ |
| `run_in_browser` (Playwright driver for stub pages) | ✅ | ✅ | ✅ |
| `collect_errors` (JS exceptions, console.error, fx:error, status) | ✅ | ✅ | ✅ |
| Gallery doubles as a browser test (no JS errors) | ✅ | ✅ | ✅ |
| `live_app` — real ASGI app (end-to-end browser test) | ✅ | ✅ | ✅ |
| pytest fixtures | ✅ | ⬜ | ⬜ |

## Showcase / docs (GitHub Pages)

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `@component.example` / `example=` kwarg + source capture (registry) | ✅ | ✅ | ✅ |
| Gallery chrome (panels, code+copy, theme toggle; phone frame later) | ✅ | ✅ | ✅ |
| Static build (`python -m iris.gallery build`) | ✅ | ✅ | ✅ |
| Tests page (`tests.html`): `@browser_example` demos as live iframes + source | ✅ | ✅ | ✅ |
| Frameworks page (`frameworks.html`): FastAPI integration examples | ✅ | ✅ | ✅ |
| GitHub Pages workflow (`.github/workflows/pages.yml`) | ✅ | ✅ | ⬜ |

## Project / infra

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `pyproject.toml` + packaging (extras: `test`) | ✅ | ✅ | ✅ |
| `README.md` | ✅ | ✅ | ⬜ |
| `examples/fastapi_app` reference app | ✅ | ⬜ | ⬜ |
