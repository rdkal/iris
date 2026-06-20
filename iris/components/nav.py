"""Navigation components. See DESIGN.md §5.

The app-shell pieces emit fixi attributes (``fx-action`` / ``fx-target`` /
``fx-push-url``) so tabs and links swap the main region instead of full reloads.
Render the host page with ``Page(fixi=True)`` to load fixi + iris-fixi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ..core import classes, component, root
from ..html import h

__all__ = ["Header", "NavLink", "Tab", "Tabs", "AppShell", "Breadcrumbs"]

#: CSS selector for the app shell's swappable main region.
MAIN = "[data-iris-main]"


@dataclass(frozen=True)
class Tab:
    """A tab/nav destination: a label, the URL to swap in, and an optional icon."""

    label: str
    src: str
    icon: str | None = None


@component
def Header(children: Any = None, *, title: Any = None, **attrs: Any) -> Any:
    return root(h.header, "header", **attrs)[
        h.div(".header-title")[title] if title is not None else None,
        children,
    ]


@component
def NavLink(children: Any, *, href: str, target: str = MAIN, swap: str = "innerHTML",
            push: bool = True, **attrs: Any) -> Any:
    """A fixi-driven link that swaps ``target`` with the response from ``href``.

    Renders a real ``<a href>`` too, so it works without JS and is shareable.
    """

    if push:
        attrs.setdefault("fx_push_url", True)
    return root(
        h.a, "navlink",
        href=href, fx_action=href, fx_target=target, fx_swap=swap, **attrs,
    )[children]


@component
def Tabs(children: Any = None, *, tabs: Iterable[Tab] = (), active: str | None = None,
         target: str = MAIN, **attrs: Any) -> Any:
    def render_tab(tab: Tab) -> Any:
        is_active = active in (tab.label, tab.src)
        return h.a(
            class_=classes("tab", {"active": is_active}),
            href=tab.src, fx_action=tab.src, fx_target=target,
            fx_swap="innerHTML", fx_push_url=True,
            aria_current="page" if is_active else None,
        )[
            h.span(".tab-icon")[tab.icon] if tab.icon else None,
            h.span(".tab-label")[tab.label],
        ]

    return root(h.nav, "tabs", **attrs)[(render_tab(t) for t in tabs)]


@component
def AppShell(children: Any = None, *, title: Any = None, tabs: Iterable[Tab] = (),
             active: str | None = None, **attrs: Any) -> Any:
    """Persistent header + swappable main region + bottom tab bar (side rail on
    wide screens).  ``children`` is the initial main content."""

    tabs = list(tabs)
    return root(h.div, "appshell", **attrs)[
        Header(title=title) if title is not None else None,
        h.main(".appshell-main", data_iris_main=True)[children],
        Tabs(tabs=tabs, active=active) if tabs else None,
    ]


@component
def Breadcrumbs(children: Any = None, *, items: Iterable[Any] = (), **attrs: Any) -> Any:
    """Items are ``(label, href)`` pairs (links) or plain labels (current page)."""

    items = list(items)
    nodes: list[Any] = []
    for i, item in enumerate(items):
        if i:
            nodes.append(h.span(".crumb-sep", aria_hidden="true")["/"])
        if isinstance(item, (tuple, list)):
            label, href = item
            nodes.append(h.a(href=href)[label])
        else:
            nodes.append(h.span(".crumb-current")[item])
    return root(h.nav, "breadcrumbs", aria_label="Breadcrumb", **attrs)[nodes, children]


# --- Examples ------------------------------------------------------------ #


@NavLink.example("Nav link")
def _():
    return NavLink(href="/search")["Search"]


@Tabs.example("Bottom tabs")
def _():
    return Tabs(active="Home", tabs=[
        Tab("Home", "/home", icon="●"),
        Tab("Search", "/search", icon="○"),
        Tab("Profile", "/me", icon="◐"),
    ])


@Breadcrumbs.example("Breadcrumbs")
def _():
    return Breadcrumbs(items=[("Home", "/"), ("Library", "/library"), "Article"])


@AppShell.example("App shell")
def _():
    return AppShell(title="iris", active="Home", tabs=[
        Tab("Home", "/home", icon="●"),
        Tab("Search", "/search", icon="○"),
        Tab("Profile", "/me", icon="◐"),
    ])[h.p["Main content swaps here when a tab is tapped."]]
