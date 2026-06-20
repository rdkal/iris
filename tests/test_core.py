"""Tests for the @component convention, rendering, and is_fx."""

from __future__ import annotations

import pytest

from iris import component, h, is_fx, render, render_stream, root


@component
def Btn(children, *, variant=None, **attrs):
    return root(h.button, "btn", **attrs)[children]


@component
def Boxed(children, *, title=None):
    return h.section[h.h2[title] if title else None, children]


def test_children_only_call():
    assert render(Btn["Save"]) == '<button class="btn">Save</button>'


def test_props_then_children():
    assert render(Btn(disabled=True)["Save"]) == '<button class="btn" disabled>Save</button>'


def test_selector_class_merges_with_base():
    out = render(Btn(".primary")["Save"])
    assert out == '<button class="btn primary">Save</button>'


def test_id_selector():
    assert 'id="go"' in render(Btn("#go")["Save"])


def test_passthrough_attrs_are_rendered():
    out = render(Btn(".primary", fx_action="/order")["Save"])
    assert 'fx-action="/order"' in out
    assert 'class="btn primary"' in out


def test_bound_renders_without_children():
    assert render(Boxed(title="Hi")) == "<section><h2>Hi</h2></section>"


def test_comprehension_children():
    out = render(h.ul[(h.li[x] for x in "ab")])
    assert out == "<ul><li>a</li><li>b</li></ul>"


def test_nested_components_compose():
    out = render(Boxed(title="T")[Btn["x"]])
    assert out == '<section><h2>T</h2><button class="btn">x</button></section>'


def test_string_children_are_escaped():
    assert "&lt;script&gt;" in render(Btn["<script>"])


def test_render_stream_matches_render():
    node = Boxed(title="T")[Btn["x"]]
    assert "".join(render_stream(node)) == render(node)


def test_non_string_selector_rejected():
    with pytest.raises(TypeError):
        Btn(123)["x"]


@pytest.mark.parametrize(
    "headers,expected",
    [
        ({"fx-request": "true"}, True),
        ({"FX-Request": "true"}, True),
        ({"Fx-Request": "TRUE"}, True),
        ({"fx-request": "false"}, False),
        ({"other": "true"}, False),
        ({}, False),
    ],
)
def test_is_fx(headers, expected):
    assert is_fx(headers) is expected


def test_is_fx_with_get_only_mapping():
    class Headers:
        def __init__(self, d):
            self._d = {k.lower(): v for k, v in d.items()}

        def get(self, key, default=None):
            return self._d.get(key.lower(), default)

    assert is_fx(Headers({"FX-Request": "true"})) is True
    assert is_fx(Headers({"x": "y"})) is False
