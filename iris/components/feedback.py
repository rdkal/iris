"""Feedback components — loading, status, progress. See DESIGN.md §3."""

from __future__ import annotations

from typing import Any

from ..core import component, root
from ..html import h
from .layout import Stack

__all__ = ["Spinner", "Skeleton", "Banner", "Progress"]


@component
def Spinner(children: Any = None, *, label: str = "Loading…", **attrs: Any) -> Any:
    return root(h.span, "spinner", role="status", aria_label=label, **attrs)[children]


@Spinner.example("Spinner")
def _():
    return Spinner()


@component
def Skeleton(children: Any = None, *, width: str | None = None,
             height: str | None = None, **attrs: Any) -> Any:
    decls = []
    if width:
        decls.append(f"width:{width}")
    if height:
        decls.append(f"height:{height}")
    if decls:
        existing = attrs.pop("style", None)
        head = [str(existing).rstrip(";")] if existing else []
        attrs["style"] = "; ".join(head + decls)
    return root(h.span, "skeleton", **attrs)[children]


@Skeleton.example("Placeholder")
def _():
    return Stack(gap=1)[
        Skeleton(width="60%", height="1rem"),
        Skeleton(width="100%", height="1rem"),
        Skeleton(width="80%", height="1rem"),
    ]


@component
def Banner(children: Any, *, role: str = "status", **attrs: Any) -> Any:
    return root(h.div, "banner", role=role, **attrs)[children]


@Banner.example("Variants")
def _():
    return Stack(gap=2)[
        Banner(".info")["Heads up — this is informational."],
        Banner(".success")["Saved successfully."],
        Banner(".warn")["Careful with this action."],
        Banner(".error", role="alert")["Something went wrong."],
    ]


@component
def Progress(children: Any = None, *, value: float | None = None,
             max: float = 100, **attrs: Any) -> Any:
    if value is not None:
        attrs["value"] = value
    return root(h.progress, "progress", max=max, **attrs)[children]


@Progress.example("Progress")
def _():
    return Progress(value=66)
