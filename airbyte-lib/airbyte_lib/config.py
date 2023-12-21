"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

from pydantic import BaseModel
# from overrides import EnforceOverrides


class CacheConfigBase(BaseModel):  # TODO: meta=EnforceOverrides (Pydantic doesn't like it currently)
    pass
