"""Form components. See DESIGN.md §3.

Only ``Button`` for now; inputs land in a later slice.  Forms themselves need no
special machinery — a ``<form>`` with ``fx_*`` attributes is just htpy + fixi.
"""

from __future__ import annotations

from typing import Any

from ..core import component, root
from ..html import h
from .layout import Row

__all__ = ["Button"]


@component
def Button(children: Any, *, type: str = "button", **attrs: Any) -> Any:
    return root(h.button, "btn", type=type, **attrs)[children]


@Button.example("Variants")
def _():
    return Row(gap=2)[
        Button(".primary")["Save"],
        Button(".ghost")["Cancel"],
        Button(".danger")["Delete"],
    ]
