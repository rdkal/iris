"""Tests for the component example mechanism (the gallery data layer)."""

from __future__ import annotations

import iris  # noqa: F401  (import registers component examples)
from iris import component, h, registered_components, render, root


def test_registered_components_have_examples():
    comps = {c.name for c in registered_components()}
    # a representative spread across families
    for name in ["Card", "Button", "Banner", "Table", "Stack", "Tag"]:
        assert name in comps


def test_every_example_renders_and_has_source():
    for c in registered_components():
        assert c.examples, f"{c.name} registered with no examples"
        for ex in c.examples:
            assert ex.source.strip()
            html = ex.render()
            assert isinstance(html, str) and html


def test_example_source_strips_return_and_decorator():
    @component
    def Widget(children, **attrs):
        return root(h.div, "widget", **attrs)[children]

    @Widget.example("Demo")
    def _():
        return Widget["hello"]

    ex = Widget.examples[0]
    assert ex.title == "Demo"
    assert ex.source == 'Widget["hello"]'
    assert ex.render() == '<div class="widget">hello</div>'


def test_example_kwarg_on_decorator():
    def usage():
        return Boxed["x"]

    @component(example=usage)
    def Boxed(children, **attrs):
        return root(h.div, "boxed", **attrs)[children]

    assert len(Boxed.examples) == 1
    assert Boxed.examples[0].render() == '<div class="boxed">x</div>'


def test_bare_example_decorator_uses_func_name():
    @component
    def Thing(children, **attrs):
        return root(h.span, "thing", **attrs)[children]

    @Thing.example
    def primary():
        return Thing["t"]

    assert Thing.examples[0].title == "primary"
