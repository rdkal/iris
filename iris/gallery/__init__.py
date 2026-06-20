"""Static showcase gallery, built from the component example registry.

The gallery is built *with* iris (dogfooding).  ``registered_components()`` is
the data layer: every ``@Comp.example`` contributes a live render + its source.

Build it::

    python -m iris.gallery build -o _site
"""

from __future__ import annotations

from .build import build, render_frameworks, render_gallery, render_tests

__all__ = ["build", "render_gallery", "render_tests", "render_frameworks"]
