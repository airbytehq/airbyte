from typing import Any, Dict

class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "account_token": "Fleetio Account Token",
            "api_token": "Fleetio API Token"
        }
    
    def with_account_token(
            self,
            account_token: str
    ) -> "ConfigBuilder":
        self._config["account_token"] = account_token
        return self

    def with_api_token(
            self,
            api_token: str
    ) -> "ConfigBuilder":
        self._config["api_token"] = api_token
        return self
    
    def build(self) -> Dict[str, Any]:
        return self._config