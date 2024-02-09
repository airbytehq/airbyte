# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Define base Config interface, used by Caches and also File Writers (Processors)."""

from __future__ import annotations

from pydantic import BaseModel


class CacheConfigBase(
    BaseModel
):  # TODO: meta=EnforceOverrides (Pydantic doesn't like it currently.)
    pass
