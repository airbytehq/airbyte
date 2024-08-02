#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import Any, List, MutableMapping

ACCESS_TOKEN = "test_access_token"
ACCOUNT_ID = "111111111111111"

PAGE_ID = "111111111111111"
BUSINESS_ACCOUNT_ID = "222222222222222"
ACCOUNTS_FIELDS = ["id", "instagram_business_account"]
START_DATE = "2022-09-01T00:00:00Z"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "access_token": ACCESS_TOKEN,
            "start_date": START_DATE,
        }

    def build(self) -> MutableMapping[str, Any]:
        return self._config
