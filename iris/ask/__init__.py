"""iris.ask — build forms from a Pydantic model, the convenient way.

`ask.form(Model, action="/x")` renders a ``<form>`` (a ``Field`` + control per
model field, types mapped to input types) that posts via fixi.  There is **no
server-side error rendering**: your FastAPI handler just validates with Pydantic,
FastAPI returns its default ``422`` JSON on failure, and ``iris-ask.js`` (bundled
by ``Page(fixi=True)``) maps those errors onto the inputs.  It's plain htpy +
fixi + FastAPI conventions underneath — inspect the output, drop down anytime.
"""

from __future__ import annotations

import datetime as _dt
import enum
import types
import typing
from typing import Any, Mapping

from ..components import Button, Checkbox, Field, Form, Input, Select
from ..html import h

__all__ = ["form"]


def _unwrap_optional(annotation: Any) -> Any:
    origin = typing.get_origin(annotation)
    if origin is typing.Union or origin is getattr(types, "UnionType", ()):
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation


def _label(name: str, field: Any) -> str:
    return getattr(field, "title", None) or name.replace("_", " ").capitalize()


def _input_type(name: str, annotation: Any) -> str:
    if annotation in (int, float):
        return "number"
    type_name = getattr(annotation, "__name__", "")
    if type_name == "EmailStr" or "email" in name.lower():
        return "email"
    if type_name == "SecretStr" or "password" in name.lower():
        return "password"
    if annotation is _dt.datetime:
        return "datetime-local"
    if annotation is _dt.date:
        return "date"
    if annotation is _dt.time:
        return "time"
    return "text"


def _control(name: str, annotation: Any, value: Any) -> Any:
    origin = typing.get_origin(annotation)
    if origin is typing.Literal:
        return Select(name=name, options=list(typing.get_args(annotation)), value=value)
    if isinstance(annotation, type) and issubclass(annotation, enum.Enum):
        return Select(name=name, options=[(e.value, e.name) for e in annotation], value=value)
    return Input(name=name, type=_input_type(name, annotation), value=value)


def _render_field(name: str, field: Any, value: Any) -> Any:
    annotation = _unwrap_optional(field.annotation)
    label = _label(name, field)
    if annotation is bool:
        return Checkbox(name=name, label=label, checked=bool(value))
    return Field(label=label, name=name)[_control(name, annotation, value)]


def form(
    model: Any,
    *,
    action: str,
    method: str = "post",
    submit: Any = "Submit",
    target: str | None = None,
    swap: str | None = None,
    values: Mapping[str, Any] | None = None,
    **attrs: Any,
) -> Any:
    """Render a form from a Pydantic model.

    ``model`` is a Pydantic ``BaseModel`` subclass; one ``Field`` is generated
    per ``model_fields`` entry.  ``values`` pre-fills inputs.  Extra ``fx_*``
    attributes pass through to the ``<form>``.
    """

    values = values or {}
    if target is not None:
        attrs.setdefault("fx_target", target)
    if swap is not None:
        attrs.setdefault("fx_swap", swap)
    # Server (Pydantic) is the source of truth — disable browser constraint
    # validation so submissions always reach the handler.
    attrs.setdefault("novalidate", True)

    fields = [
        _render_field(name, field, values.get(name))
        for name, field in model.model_fields.items()
    ]
    return Form(action=action, method=method, **attrs)[
        fields,
        Button(".primary", type="submit")[submit],
    ]
