from datetime import datetime
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "account_id": "any account id",
            "credentials": {"api_token": "any api token"},
            "replication_start_date": "2017-01-25T00:00:00Z",
        }

    def with_replication_start_date(self, replication_start_date: datetime) -> "ConfigBuilder":
        self._config["replication_start_date"] = replication_start_date.isoformat()
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
