# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, MutableMapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "api_key": "test_api_key",
            "api_secret": "test_api_secret",
            "shop": "airbyte.store",
            "start_date": "2017-01-01",
        }

    def build(self) -> MutableMapping[str, Any]:
        return self._config
