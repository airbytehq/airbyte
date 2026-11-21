# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional


class ConfigBuilder:
    """Builder for source-fxmacrodata test configurations. Keyless by default."""

    def __init__(self) -> None:
        self._api_key: Optional[str] = None
        self._currencies: List[str] = ["USD"]
        self._indicators: List[str] = ["policy_rate"]
        self._start_date: Optional[str] = None
        self._forex_pairs: List[str] = []

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def with_currencies(self, *currencies: str) -> "ConfigBuilder":
        self._currencies = list(currencies)
        return self

    def with_indicators(self, *indicators: str) -> "ConfigBuilder":
        self._indicators = list(indicators)
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def with_forex_pairs(self, *pairs: str) -> "ConfigBuilder":
        self._forex_pairs = list(pairs)
        return self

    def build(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "currencies": self._currencies,
            "indicators": self._indicators,
            "forex_pairs": self._forex_pairs,
        }
        if self._api_key:
            config["api_key"] = self._api_key
        if self._start_date:
            config["start_date"] = self._start_date
        return config
