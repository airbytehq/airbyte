# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

from unit_tests.conftest import CONFIG


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: dict[str, Any] = dict(CONFIG)

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_end_date(self, end_date: str) -> "ConfigBuilder":
        self._config["end_date"] = end_date
        return self

    def with_num_workers(self, num_workers: int) -> "ConfigBuilder":
        self._config["num_workers"] = num_workers
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
