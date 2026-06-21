"""Overlay components — Modal, Drawer, Menu, Popover, Toast.

Modal/Drawer/Menu/Popover use the native Popover API (``popover`` +
``popovertarget``), so they open and close with **zero JavaScript** — including
light-dismiss (click-outside / Esc) and top-layer stacking. Each renders a
trigger button wired to the overlay by a generated id.
"""

from __future__ import annotations

from secrets import token_hex
from typing import Any

from ..core import classes, component, root
from ..html import h
from .forms import Button
from .layout import Stack

__all__ = ["Modal", "Drawer", "Menu", "Popover", "Toast"]


def _auto_id(prefix: str) -> str:
    return f"{prefix}-{token_hex(4)}"


def _close_button(target: str) -> Any:
    return h.button(
        ".overlay-close", type="button",
        popovertarget=target, popovertargetaction="hide", aria_label="Close",
    )["×"]


@component
def Modal(children: Any, *, trigger: Any, title: Any = None, id: str | None = None,
          **attrs: Any) -> Any:
    pid = id or _auto_id("modal")
    return h.fragment[
        Button(popovertarget=pid)[trigger],
        root(h.div, "modal", id=pid, popover="auto", **attrs)[
            h.div(".modal-card")[
                h.div(".overlay-head")[
                    h.div(".overlay-title")[title] if title is not None else None,
                    _close_button(pid),
                ],
                h.div(".overlay-body")[children],
            ]
        ],
    ]


@component
def Drawer(children: Any, *, trigger: Any, side: str = "bottom", title: Any = None,
           id: str | None = None, **attrs: Any) -> Any:
    pid = id or _auto_id("drawer")
    return h.fragment[
        Button(popovertarget=pid)[trigger],
        root(h.div, "drawer", f"drawer-{side}", id=pid, popover="auto", **attrs)[
            h.div(".overlay-head")[
                h.div(".overlay-title")[title] if title is not None else None,
                _close_button(pid),
            ],
            h.div(".overlay-body")[children],
        ],
    ]


@component
def Menu(children: Any, *, trigger: Any, id: str | None = None, **attrs: Any) -> Any:
    pid = id or _auto_id("menu")
    return h.fragment[
        Button(popovertarget=pid, style=f"anchor-name:--{pid}")[trigger],
        root(h.div, "menu", id=pid, popover="auto",
             style=f"position-anchor:--{pid}", **attrs)[children],
    ]


@component
def Popover(children: Any, *, trigger: Any, id: str | None = None, **attrs: Any) -> Any:
    pid = id or _auto_id("popover")
    return h.fragment[
        Button(popovertarget=pid, style=f"anchor-name:--{pid}")[trigger],
        root(h.div, "popover", id=pid, popover="auto",
             style=f"position-anchor:--{pid}", **attrs)[children],
    ]


@component
def Toast(children: Any, **attrs: Any) -> Any:
    """A notification box.

    On its own it's a static inline box. For floating, auto-dismissing
    notifications, place it in a fixed ``.toast-region`` (e.g. a fragment fixi
    swaps in): ``h.div(".toast-region")[Toast(".success")["Saved"]]``.
    """

    return root(h.div, "toast", role="status", **attrs)[children]


# --- Examples ------------------------------------------------------------ #


@Modal.example("Modal")
def _():
    return Modal(trigger="Open modal", title="Delete item?")[
        h.p["This action cannot be undone."],
    ]


@Drawer.example("Drawer (bottom sheet)")
def _():
    return Drawer(trigger="Open drawer", title="Filters", side="bottom")[
        h.p["Drawer content slides in from the edge."],
    ]


@Menu.example("Menu")
def _():
    return Menu(trigger="Actions")[
        h.button(".menu-item")["Edit"],
        h.button(".menu-item")["Duplicate"],
        h.button(".menu-item")["Delete"],
    ]


@Popover.example("Popover")
def _():
    return Popover(trigger="Details")[
        h.p["A small anchored panel of extra content."],
    ]


@Toast.example("Toast")
def _():
    return Toast(".success")["Saved successfully."]
