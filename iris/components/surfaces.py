"""Surface components — cards, sheets, panels. See DESIGN.md §3."""

from __future__ import annotations

from typing import Any

from ..core import component, root
from ..html import h

__all__ = ["Card", "Sheet", "Panel"]


@component
def Card(children: Any, **attrs: Any) -> Any:
    return root(h.div, "card", **attrs)[children]


@component
def Sheet(children: Any, **attrs: Any) -> Any:
    return root(h.div, "sheet", **attrs)[children]


@component
def Panel(children: Any, **attrs: Any) -> Any:
    return root(h.div, "panel", **attrs)[children]
