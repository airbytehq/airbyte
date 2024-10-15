# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Connector info classes for PyAirbyte.

Used for telemetry and logging.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RuntimeInfoBase:
    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class WriterRuntimeInfo(RuntimeInfoBase):
    type: str
    config_hash: str | None = None


@dataclass(kw_only=True)
class ConnectorRuntimeInfo(RuntimeInfoBase):
    name: str
    executor_type: str | None = None
    version: str | None = None
    config_hash: str | None = None
