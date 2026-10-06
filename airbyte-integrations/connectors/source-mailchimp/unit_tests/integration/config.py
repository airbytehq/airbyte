# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {"credentials": {"auth_type": "apikey", "apikey": "Mailchimp_token-us10"}, "data_center": "us10"}

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_datetime.isoformat()[:-3] + "Z"
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
