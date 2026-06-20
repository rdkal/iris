"""Core of iris: the ``@component`` calling convention, rendering, and helpers.

A component is a function ``func(children, **props) -> Node`` wrapped by
:func:`component`.  The wrapper gives it htpy's two-step calling convention:

    Comp(*selectors, **props)[children]   # props then children
    Comp[children]                        # children only
    Comp(*selectors, **props)             # no children (renderable as-is)

``*selectors`` are htpy-style strings (``".primary"``, ``"#main"``) that are
parsed into ``class``/``id`` and merged with any ``class_`` prop, so the result
composes natively with htpy.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Callable

import htpy
from htpy import Node

__all__ = [
    "component",
    "render",
    "render_stream",
    "is_fx",
    "classes",
    "root",
]

_SELECTOR = re.compile(r"([#.])([^#.]+)")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, Mapping)):
        return [value]
    if isinstance(value, Iterable):
        return list(value)
    return [value]


def classes(*values: Any) -> list[Any]:
    """Flatten class fragments (strings, lists, dicts) into one htpy class list.

    ``None``/empty fragments drop out; dict and falsey entries are handled by
    htpy itself, so ``classes("btn", extra, {"on": flag})`` is safe.
    """

    out: list[Any] = []
    for value in values:
        out.extend(_as_list(value))
    return out


def _parse_selectors(selectors: tuple[Any, ...]) -> tuple[list[str], str | None]:
    """Turn positional selector strings into (class list, id)."""

    cls: list[str] = []
    el_id: str | None = None
    for selector in selectors:
        if not isinstance(selector, str):
            raise TypeError(
                f"component selectors must be strings like '.primary'/'#id', "
                f"got {selector!r}"
            )
        for kind, name in _SELECTOR.findall(selector):
            if kind == "#":
                el_id = name
            else:
                cls.append(name)
    return cls, el_id


def root(tag: Any, *base: str, **attrs: Any) -> Any:
    """Build a component's root element, merging ``base`` classes with ``class_``.

    Authors use this so pass-through ``class_`` from the call site is combined
    with the component's own classes instead of overriding them::

        root(h.div, "stack", style=f"--gap:{gap}", **attrs)[children]
    """

    merged = classes(*base, attrs.pop("class_", None))
    return tag(class_=merged, **attrs)


class _Bound:
    """A component with props captured, awaiting an optional ``[children]``."""

    __slots__ = ("_component", "_selectors", "_props")

    def __init__(self, component: "Component", selectors: tuple[Any, ...], props: dict[str, Any]):
        self._component = component
        self._selectors = selectors
        self._props = props

    def __getitem__(self, children: Node) -> Any:
        return self._component._build(children, self._selectors, self._props)

    # Renderable with no children (e.g. ArticleCard(...) with no [...]).
    def _render(self) -> Any:
        return self._component._build(None, self._selectors, self._props)

    def __call__(self) -> Any:  # htpy treats Callable[[], Node] as a node
        return self._render()

    def __str__(self) -> str:
        return str(self._render())

    def iter_chunks(self, context: Any = None) -> Iterator[str]:
        return self._render().iter_chunks(context)

    def __repr__(self) -> str:
        return f"<iris component {self._component.name}>"


class Component:
    """Wraps ``func(children, **props)`` with the htpy calling convention."""

    def __init__(self, func: Callable[..., Node]):
        self._func = func
        self.name = getattr(func, "__name__", "component")
        self.__doc__ = func.__doc__
        self.__wrapped__ = func

    def __call__(self, *selectors: Any, **props: Any) -> _Bound:
        return _Bound(self, selectors, props)

    def __getitem__(self, children: Node) -> Any:
        return self._build(children, (), {})

    def _build(self, children: Node, selectors: tuple[Any, ...], props: dict[str, Any]) -> Any:
        cls, el_id = _parse_selectors(selectors)
        props = dict(props)
        if cls:
            props["class_"] = classes(cls, props.get("class_"))
        if el_id is not None:
            props.setdefault("id", el_id)
        return self._func(children, **props)

    def __repr__(self) -> str:
        return f"<iris component {self.name}>"


def component(func: Callable[..., Node]) -> Component:
    """Decorator turning a ``func(children, **props)`` into an iris component."""

    return Component(func)


def _to_node(node: Node) -> Node:
    # _Bound is rendered via its __call__; wrap everything in a fragment so
    # arbitrary nodes (lists, generators, bound components) render uniformly.
    return htpy.fragment[node]


def render(node: Node) -> str:
    """Render a node tree to an HTML string."""

    return str(_to_node(node))


def render_stream(node: Node) -> Iterator[str]:
    """Render a node tree to an iterator of HTML chunks (low TTFB)."""

    return _to_node(node).iter_chunks()


def is_fx(headers: Mapping[str, str] | Any) -> bool:
    """Return True if ``headers`` indicate a fixi request (``FX-Request: true``).

    Accepts any case-insensitive or plain mapping of headers (FastAPI/Starlette
    ``Headers``, Werkzeug, or a plain ``dict``).
    """

    value: Any = None
    getter = getattr(headers, "get", None)
    if callable(getter):
        value = getter("fx-request")
        if value is None:
            value = getter("FX-Request")
    if value is None:
        try:
            for key, val in headers.items():  # type: ignore[union-attr]
                if str(key).lower() == "fx-request":
                    value = val
                    break
        except AttributeError:
            return False
    return str(value).lower() == "true"
