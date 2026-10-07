# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, Mapping

from unit_tests.conftest import build_config


class ConfigBuilder:
    """Builder for connector configs used by mock-server tests."""

    def __init__(self) -> None:
        self._config = dict(build_config())

    def with_value(self, name: str, value: Any) -> "ConfigBuilder":
        self._config[name] = value
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
