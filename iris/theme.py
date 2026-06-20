"""Theme tokens and stylesheet generation.

The entire look is driven by a small set of CSS custom properties (see
:class:`Theme`).  Everything else is *derived* from them in ``iris.css``.  Dark
is the default; :data:`LIGHT` is the same variables with different values.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from importlib import resources

__all__ = ["Theme", "DARK", "LIGHT", "stylesheet"]


@dataclass(frozen=True)
class Theme:
    """The ~12 tokens that define the design system.

    Override a few to re-theme::

        Theme(accent="#22d3aa", radius="0.25rem")
    """

    # color
    bg: str = "#0b0c0e"
    surface: str = "#15171b"
    text: str = "#e7e9ec"
    muted: str = "#8b9099"
    accent: str = "#6ea8fe"
    border: str = "#262a31"
    # shape & rhythm
    space: str = "0.5rem"
    radius: str = "0.75rem"
    font: str = "system-ui, sans-serif"
    measure: str = "38rem"

    def variables(self) -> dict[str, str]:
        """Token values keyed by their CSS custom-property name."""

        return {f"--{f.name}": getattr(self, f.name) for f in fields(self)}

    def root_css(self, selector: str = ":root") -> str:
        """A CSS rule assigning the tokens to ``selector``."""

        body = "\n".join(f"  {name}: {value};" for name, value in self.variables().items())
        return f"{selector} {{\n{body}\n}}"


#: Default dark theme.
DARK = Theme()

#: Light theme — same variables, lighter values.
LIGHT = Theme(
    bg="#ffffff",
    surface="#f5f6f8",
    text="#13151a",
    muted="#5b6470",
    accent="#2563eb",
    border="#e3e6ea",
)


def _base_css() -> str:
    return resources.files("iris").joinpath("static/iris.css").read_text(encoding="utf-8")


def stylesheet(theme: Theme = DARK, *, light: Theme | None = LIGHT) -> str:
    """Return a complete stylesheet: token variables + the iris base styles.

    ``theme`` sets the default (``:root``) tokens; ``light`` (if given) is
    emitted under ``[data-theme="light"]`` for a toggle.  Pass ``light=None`` to
    omit the light block.
    """

    parts = [theme.root_css(":root")]
    if light is not None:
        parts.append(light.root_css('[data-theme="light"]'))
    parts.append(_base_css())
    return "\n\n".join(parts)
