# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-waiteraid test configurations."""

    def __init__(self) -> None:
        self._auth_hash: str = "test-auth-hash"
        self._restid: str = "1234"
        self._start_date: str = "2026-09-01"

    def with_auth_hash(self, auth_hash: str) -> "ConfigBuilder":
        self._auth_hash = auth_hash
        return self

    def with_restid(self, restid: str) -> "ConfigBuilder":
        self._restid = restid
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return {"auth_hash": self._auth_hash, "restid": self._restid, "start_date": self._start_date}
