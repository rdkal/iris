"""Layout primitives — mobile-first. See DESIGN.md §3 and §5."""

from __future__ import annotations

from typing import Any

from ..core import component, raw, root
from ..html import h
from ..theme import DARK, Theme, stylesheet

__all__ = [
    "Page",
    "Container",
    "Stack",
    "Row",
    "Grid",
    "Center",
    "Divider",
    "Spacer",
]


def _style(existing: Any, **vars: Any) -> str | None:
    """Merge an existing ``style`` string with ``--name: value`` assignments.

    Variables whose value is ``None`` are skipped, so callers can pass optional
    props directly: ``_style(attrs.pop("style", None), gap=gap)``.
    """

    parts: list[str] = []
    if existing:
        parts.append(str(existing).rstrip(";"))
    for name, value in vars.items():
        if value is not None:
            parts.append(f"--{name}: {value}")
    return "; ".join(parts) if parts else None


def _box(tag: Any, base: str, children: Any, attrs: dict[str, Any], **css_vars: Any) -> Any:
    style = _style(attrs.pop("style", None), **css_vars)
    if style is not None:
        attrs["style"] = style
    return root(tag, base, **attrs)[children]


@component
def Page(children: Any, *, title: str | None = None, theme: Theme = DARK,
         lang: str = "en", **attrs: Any) -> Any:
    """A full, self-contained HTML document with the iris stylesheet inlined.

    Mobile-first: ships the ``viewport`` meta so phones render at device width.
    ``**attrs`` are applied to ``<body>``.
    """

    return h.html(lang=lang)[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title[title] if title else None,
            h.style[raw(stylesheet(theme))],
        ],
        root(h.body, "iris", **attrs)[children],
    ]


@component
def Container(children: Any, **attrs: Any) -> Any:
    return root(h.div, "container", **attrs)[children]


@component
def Stack(children: Any, *, gap: float | int | None = None, **attrs: Any) -> Any:
    return _box(h.div, "stack", children, attrs, gap=gap)


@component
def Row(children: Any, *, gap: float | int | None = None, **attrs: Any) -> Any:
    return _box(h.div, "row", children, attrs, gap=gap)


@component
def Grid(children: Any, *, cols: int | None = None, gap: float | int | None = None,
         **attrs: Any) -> Any:
    return _box(h.div, "grid", children, attrs, cols=cols, gap=gap)


@component
def Center(children: Any, **attrs: Any) -> Any:
    return root(h.div, "center", **attrs)[children]


@component
def Divider(children: Any = None, **attrs: Any) -> Any:
    return root(h.hr, "divider", **attrs)


@component
def Spacer(children: Any = None, **attrs: Any) -> Any:
    return root(h.div, "spacer", **attrs)


# --- Examples (captured for the docs/gallery) ---------------------------- #


@Stack.example("Vertical stack")
def _():
    return Stack(gap=2)[h.div["One"], h.div["Two"], h.div["Three"]]


@Row.example("Row with spacer")
def _():
    return Row[h.span["Left"], Spacer, h.span(".muted")["Right"]]


@Grid.example("Responsive grid")
def _():
    return Grid(cols=3, gap=2)[(h.div(".card")[f"Item {i}"] for i in range(1, 7))]
