"""Integrations that turn an iris ``Node`` into a framework response."""

from __future__ import annotations

__all__ = ["IrisResponse"]


def __getattr__(name: str):  # pragma: no cover - thin convenience
    if name == "IrisResponse":
        from .fastapi import IrisResponse

        return IrisResponse
    raise AttributeError(name)
