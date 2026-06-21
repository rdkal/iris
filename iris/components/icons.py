"""A small inline-SVG icon set (feather-style strokes), themed via currentColor.

Icons compose anywhere a node does, e.g. ``Tab("Home", "/home", icon=Icon(name="home"))``.
"""

from __future__ import annotations

from typing import Any

from ..core import classes, component
from ..html import h
from .layout import Row

__all__ = ["Icon", "ICONS"]

# Feather Icons (MIT) — 24x24, single-path where possible.
ICONS: dict[str, str] = {
    "home": "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10",
    "search": "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z M21 21l-4.35-4.35",
    "user": "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
    "check": "M20 6L9 17l-5-5",
    "close": "M18 6L6 18 M6 6l12 12",
    "menu": "M3 12h18 M3 6h18 M3 18h18",
    "plus": "M12 5v14 M5 12h14",
    "chevron-down": "M6 9l6 6 6-6",
    "chevron-right": "M9 18l6-6-6-6",
    "bell": "M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 0 1-3.46 0",
    "heart": (
        "M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 "
        "7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
    ),
    "settings": (
        "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z "
        "M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 "
        "1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 "
        "0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 "
        "1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 "
        "0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 "
        "1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 "
        "0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 "
        "1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 "
        "0 0 0-1.51 1z"
    ),
    "trash": "M3 6h18 M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2",
}


@component
def Icon(children: Any = None, *, name: str, size: str = "1.25em", **attrs: Any) -> Any:
    if name not in ICONS:
        raise KeyError(f"unknown icon {name!r}; known: {', '.join(sorted(ICONS))}")
    return h.svg(
        class_=classes("icon", attrs.pop("class_", None)),
        width=size, height=size, viewBox="0 0 24 24",
        fill="none", stroke="currentColor", stroke_width="2",
        stroke_linecap="round", stroke_linejoin="round", aria_hidden="true", **attrs,
    )[h.path(d=ICONS[name])]


@Icon.example("Icon set")
def _():
    return Row(gap=3)[
        (Icon(name=n, size="1.5em") for n in
         ["home", "search", "user", "bell", "heart", "settings", "trash", "check"])
    ]
