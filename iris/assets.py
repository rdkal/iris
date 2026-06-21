"""Access to bundled static assets (fixi + iris JS) as inlineable markup."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

from markupsafe import Markup

__all__ = ["read_static", "fixi_js", "iris_fixi_js", "iris_test_js", "iris_ask_js"]


@lru_cache(maxsize=None)
def _read(name: str) -> str:
    return resources.files("iris").joinpath(f"static/{name}").read_text(encoding="utf-8")


def read_static(name: str) -> Markup:
    """Return a bundled ``iris/static/<name>`` file as trusted markup, safe to
    inline inside a ``<script>`` (any ``</script`` is neutralised)."""

    return Markup(_read(name).replace("</script", "<\\/script"))


def fixi_js() -> Markup:
    return read_static("fixi.js")


def iris_fixi_js() -> Markup:
    return read_static("iris-fixi.js")


def iris_test_js() -> Markup:
    return read_static("iris-test.js")


def iris_ask_js() -> Markup:
    return read_static("iris-ask.js")
