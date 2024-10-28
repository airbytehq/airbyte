# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "client_secret": "ConfigBuilder default client secret",
            "account_id": "ConfigBuilder default account id",
            "start_date": "2020-05-01T00:00:00Z",
        }

    def with_account_id(self, account_id: str) -> "ConfigBuilder":
        self._config["account_id"] = account_id
        return self

    def with_client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._config["client_secret"] = client_secret
        return self

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_datetime.isoformat()[:-13] + "Z"
        return self

    def with_lookback_window_in_days(self, number_of_days: int) -> "ConfigBuilder":
        self._config["lookback_window_days"] = number_of_days
        return self

    def with_slice_range_in_days(self, number_of_days: int) -> "ConfigBuilder":
        self._config["slice_range"] = number_of_days
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
