"""Form components. See DESIGN.md §3.

These are plain htpy + fixi under the hood — a ``Form`` is a ``<form>`` with
``fx_*`` attributes, a ``Field`` is a labelled wrapper with an error slot, etc.
The higher-level :mod:`iris.ask` package composes these from a Pydantic model.
"""

from __future__ import annotations

from typing import Any, Iterable

from ..core import component, root
from ..html import h
from .layout import Row, Stack

__all__ = [
    "Button",
    "Form",
    "Field",
    "Input",
    "Textarea",
    "Select",
    "Checkbox",
    "Switch",
]


@component
def Button(children: Any, *, type: str = "button", **attrs: Any) -> Any:
    return root(h.button, "btn", type=type, **attrs)[children]


@component
def Form(children: Any, *, action: str | None = None, method: str = "post",
         **attrs: Any) -> Any:
    """A ``<form>``. Pass ``action`` to wire a fixi submit (``fx-action``)."""

    if action is not None:
        attrs.setdefault("fx_action", action)
        attrs.setdefault("fx_method", method)
    return root(h.form, "form", **attrs)[children]


@component
def Field(children: Any, *, label: Any = None, name: str | None = None,
          error: Any = None, **attrs: Any) -> Any:
    """A labelled control with an error slot.

    The ``.field-error`` slot is filled server-side (``error=``) or by
    ``iris-ask.js`` from a FastAPI 422 response; ``.field`` gets ``.invalid``.
    """

    return root(h.div, "field", **attrs)[
        h.label(".field-label", for_=name)[label] if label is not None else None,
        children,
        h.div(".field-error")[error],
    ]


@component
def Input(children: Any = None, *, name: str | None = None, type: str = "text",
          value: Any = None, placeholder: str | None = None, **attrs: Any) -> Any:
    return root(
        h.input, "input",
        name=name, type=type, value=value, placeholder=placeholder, **attrs,
    )


@component
def Textarea(children: Any = None, *, name: str | None = None,
             placeholder: str | None = None, **attrs: Any) -> Any:
    return root(h.textarea, "input", name=name, placeholder=placeholder, **attrs)[children]


@component
def Select(children: Any = None, *, name: str | None = None,
           options: Iterable[Any] | None = None, value: Any = None, **attrs: Any) -> Any:
    """A ``<select>``. ``options`` are ``(value, label)`` pairs or plain values."""

    if options is not None:
        def opt(o: Any) -> Any:
            val, label = o if isinstance(o, (tuple, list)) else (o, o)
            return h.option(value=val, selected=(value is not None and val == value))[label]

        children = [opt(o) for o in options]
    return root(h.select, "input", name=name, **attrs)[children]


@component
def Checkbox(children: Any = None, *, name: str | None = None, label: Any = None,
             checked: bool = False, **attrs: Any) -> Any:
    return root(h.label, "checkbox")[
        h.input(type="checkbox", name=name, checked=checked, **attrs),
        h.span[label] if label is not None else children,
    ]


@component
def Switch(children: Any = None, *, name: str | None = None, label: Any = None,
           checked: bool = False, **attrs: Any) -> Any:
    return root(h.label, "switch")[
        h.input(type="checkbox", name=name, checked=checked, **attrs),
        h.span(".switch-track")[h.span(".switch-thumb")],
        h.span[label] if label is not None else children,
    ]


# --- Examples ------------------------------------------------------------ #


@Button.example("Variants")
def _():
    return Row(gap=2)[
        Button(".primary")["Save"],
        Button(".ghost")["Cancel"],
        Button(".danger")["Delete"],
    ]


@Field.example("Text field")
def _():
    return Field(label="Email", name="email")[
        Input(name="email", type="email", placeholder="you@example.com")
    ]


@Field.example("Invalid field")
def _():
    return Field(".invalid", label="Email", name="email", error="Not a valid email")[
        Input(name="email", type="email", value="nope")
    ]


@Select.example("Select")
def _():
    return Field(label="Role", name="role")[
        Select(name="role", options=["Admin", "Maintainer", "Guest"])
    ]


@Checkbox.example("Checkbox & switch")
def _():
    return Stack(gap=2)[
        Checkbox(name="terms", label="I accept the terms", checked=True),
        Switch(name="notify", label="Email notifications"),
    ]
