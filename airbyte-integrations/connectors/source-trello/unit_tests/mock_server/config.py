# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {"key": "test-key", "token": "test-token", "start_date": "2024-01-01T00:00:00Z"}

    def with_board_ids(self, board_ids: list[str]) -> "ConfigBuilder":
        self._config["board_ids"] = board_ids
        return self

    def build(self) -> dict:
        return dict(self._config)
