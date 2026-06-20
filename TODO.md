# iris — TODO

Status of every piece in [DESIGN.md](./DESIGN.md). Everything is **Designed**.
Built so far: core, theme + dark stylesheet, layout/surface/data/feedback
components + `Button`, the component **example mechanism** (`@Comp.example`
captures source + live render), and the **static gallery** (`python -m
iris.gallery build`) + GitHub Pages workflow — all with tests.

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
| `AppShell` (bottom tabs → side rail) | ✅ | ⬜ | ⬜ |
| `Header` | ✅ | ⬜ | ⬜ |
| `Tabs` / `Tab` | ✅ | ⬜ | ⬜ |
| `NavLink` | ✅ | ⬜ | ⬜ |
| `Breadcrumbs` | ✅ | ⬜ | ⬜ |

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
| `fx_*` attribute support on components | ✅ | ⬜ | ⬜ |
| Vendored `fixi.js` | ✅ | ⬜ | ⬜ |
| `iris-fixi.js` (history, polling, indicators) | ✅ | ⬜ | ⬜ |
| `is_fx()` header check (fragment vs full `Page`) | ✅ | ✅ | ✅ |

## Framework integration

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `IrisResponse` (FastAPI / Starlette, streaming) | ✅ | ⬜ | ⬜ |
| Flask / Django / WSGI `render()` adapters | ✅ | ⬜ | ⬜ |

## Testing (`iris.testing`)

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `collect_errors` (JS exceptions, console.error, fx:error, status) | ✅ | ⬜ | ⬜ |
| `serve` — isolated rendered node | ✅ | ⬜ | ⬜ |
| `live_app` — real ASGI/WSGI app | ✅ | ⬜ | ⬜ |
| pytest fixtures | ✅ | ⬜ | ⬜ |

## Showcase / docs (GitHub Pages)

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `@component.example` / `example=` kwarg + source capture (registry) | ✅ | ✅ | ✅ |
| Gallery chrome (panels, code+copy, theme toggle; phone frame later) | ✅ | ✅ | ✅ |
| Static build (`python -m iris.gallery build`) | ✅ | ✅ | ✅ |
| GitHub Pages workflow (`.github/workflows/pages.yml`) | ✅ | ✅ | ⬜ |

## Project / infra

| Item | Designed | Implemented | Tested |
| --- | :---: | :---: | :---: |
| `pyproject.toml` + packaging (extras: `test`) | ✅ | ✅ | ✅ |
| `README.md` | ✅ | ✅ | ⬜ |
| `examples/fastapi_app` reference app | ✅ | ⬜ | ⬜ |
