"""``h`` — iris's re-export of htpy.

Import iris's components and ``h`` from one place::

    from iris import Stack, Card, h

    Stack[ Card[ h.h2["Title"], h.p["Body"] ] ]

``h`` is the htpy module itself, so every raw tag (``h.div``, ``h.span``) and
helper (``h.fragment``, ``h.Node``, ``h.Context``) is available and mixes freely
with iris components.
"""

from __future__ import annotations

import htpy as h  # noqa: F401  (re-exported)

__all__ = ["h"]
