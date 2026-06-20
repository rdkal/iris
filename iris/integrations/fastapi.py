"""FastAPI / Starlette integration. See DESIGN.md §7.

``IrisResponse`` renders an iris ``Node`` and streams it as ``text/html`` using
htpy's chunked rendering for a low time-to-first-byte.  iris owns the view, the
framework owns routing; use :func:`iris.is_fx` to branch on fixi requests.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..core import render_stream

try:
    from starlette.responses import StreamingResponse
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise ModuleNotFoundError(
        "iris.integrations.fastapi requires starlette/fastapi. "
        "Install with: pip install 'iris-ui[fastapi]'"
    ) from exc

__all__ = ["IrisResponse"]


class IrisResponse(StreamingResponse):
    """A streaming ``text/html`` response rendered from an iris node."""

    def __init__(
        self,
        node: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ):
        super().__init__(
            render_stream(node),
            status_code=status_code,
            media_type="text/html",
            headers=dict(headers) if headers else None,
        )
