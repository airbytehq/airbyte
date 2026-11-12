# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self):
        self._config = {
            "auth_hash": "test-auth-hash",
            "restid": "12345",
            "start_date": "2026-09-03",
        }

    def with_auth_hash(self, auth_hash: str) -> "ConfigBuilder":
        self._config["auth_hash"] = auth_hash
        return self

    def with_restid(self, restid: str) -> "ConfigBuilder":
        self._config["restid"] = restid
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> dict:
        return dict(self._config)
