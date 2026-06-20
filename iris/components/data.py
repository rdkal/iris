"""Data-display components. See DESIGN.md §3."""

from __future__ import annotations

from typing import Any, Iterable

from ..core import component, root
from ..html import h
from .layout import Row

__all__ = ["Badge", "Tag", "Avatar", "Stat", "Empty", "List", "Table"]


@component
def Badge(children: Any, **attrs: Any) -> Any:
    return root(h.span, "badge", **attrs)[children]


@Badge.example("Badges")
def _():
    return Row(gap=1)[Badge["New"], Badge(".accent")["3"]]


@component
def Tag(children: Any, **attrs: Any) -> Any:
    return root(h.span, "tag", **attrs)[children]


@Tag.example("Tags")
def _():
    return Row(gap=1)[(Tag[t] for t in ["python", "ui", "htpy"])]


@component
def Avatar(children: Any = None, *, src: str | None = None, alt: str = "", **attrs: Any) -> Any:
    if src:
        return root(h.img, "avatar", src=src, alt=alt, **attrs)
    return root(h.span, "avatar", **attrs)[children]


@Avatar.example("Initials")
def _():
    return Row(gap=1)[Avatar["AB"], Avatar["CD"], Avatar["EF"]]


@component
def Stat(children: Any = None, *, label: str | None = None, value: Any = None, **attrs: Any) -> Any:
    return root(h.div, "stat", **attrs)[
        h.div(".stat-value")[value] if value is not None else None,
        h.div(".stat-label")[label] if label else None,
        children,
    ]


@Stat.example("KPIs")
def _():
    return Row(gap=4)[
        Stat(label="Users", value="1,204"),
        Stat(label="Revenue", value="$8.3k"),
    ]


@component
def Empty(children: Any = None, *, title: str | None = None, icon: Any = None, **attrs: Any) -> Any:
    return root(h.div, "empty", **attrs)[
        h.div(".empty-icon")[icon] if icon else None,
        h.p(".empty-title")[title] if title else None,
        children,
    ]


@Empty.example("No results")
def _():
    return Empty(title="Nothing here yet", icon="∅")["Add your first item to get started."]


@component
def List(children: Any = None, *, items: Iterable[Any] | None = None, **attrs: Any) -> Any:
    if items is not None:
        children = (h.li[item] for item in items)
    return root(h.ul, "list", **attrs)[children]


@List.example("Simple list")
def _():
    return List(items=["First item", "Second item", "Third item"])


@component
def Table(children: Any = None, *, headers: Iterable[Any] | None = None,
          rows: Iterable[Iterable[Any]] | None = None, **attrs: Any) -> Any:
    head = h.thead[h.tr[(h.th[c] for c in headers)]] if headers else None
    body = (
        h.tbody[(h.tr[(h.td[c] for c in row)] for row in rows)]
        if rows is not None
        else children
    )
    return root(h.table, "table", **attrs)[head, body]


@Table.example("Data table")
def _():
    return Table(
        headers=["Name", "Role"],
        rows=[["Ada", "Admin"], ["Linus", "Maintainer"]],
    )
