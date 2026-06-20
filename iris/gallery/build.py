"""Render the component gallery to a self-contained static HTML page."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Importing the package registers every component's examples.
import iris  # noqa: F401
from ..core import Component, Example, raw, registered_components
from ..html import h
from ..theme import DARK, Theme, stylesheet

__all__ = ["render_gallery", "build"]


GALLERY_CSS = """
.gallery-main { max-width: 60rem; margin-inline: auto; }

.gallery-header {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: calc(var(--space) * 2) calc(var(--space) * 3);
  background: color-mix(in oklab, var(--bg), transparent 15%);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}
.gallery-header h1 { font-size: 1.1rem; }
.gallery-header .sub { color: var(--muted); font-size: 0.85em; }

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

.panel-card { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; margin-top: 1rem; }
.panel-head {
  padding: 0.6rem 1rem; font-size: 0.78em; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--muted); border-bottom: 1px solid var(--border); background: var(--surface);
}
.panel-preview { padding: calc(var(--space) * 3); }

.panel-code { position: relative; border-top: 1px solid var(--border); }
.panel-code pre {
  margin: 0; padding: 1rem; overflow: auto; font-size: 0.85em; line-height: 1.5;
  background: color-mix(in oklab, var(--bg), black 35%);
}
.panel-code .copy {
  position: absolute; top: 0.5rem; right: 0.5rem;
  font-size: 0.75em; padding: 0.2rem 0.6rem;
  border: 1px solid var(--border); border-radius: 0.4rem;
  background: var(--surface); color: var(--muted); cursor: pointer;
}
.panel-code .copy:hover { color: var(--text); }
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
        h.p(".component-doc")[component.__doc__.strip()] if component.__doc__ else None,
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
            h.header(".gallery-header")[
                h.div[
                    h.h1["iris"],
                    h.div(".sub")["Live render + the exact source for every component."],
                ],
                h.button(".theme-btn", id="theme-toggle", type="button")["Toggle theme"],
            ],
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


def build(out: str | Path = "_site", *, theme: Theme = DARK) -> Path:
    """Render the gallery to ``<out>/index.html`` and return that path."""

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    index = out_dir / "index.html"
    index.write_text(render_gallery(theme), encoding="utf-8")
    return index
