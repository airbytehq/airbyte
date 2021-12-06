from typing import Any, Dict, Optional

from destination_netsuite.netsuite.configuration import Config, cached_property
from destination_netsuite.netsuite.rest import NetSuiteRestApi

__all__ = ("NetSuite",)

class NetSuite:
    def __init__(
        self,
        config: Config,
        *,
        rest_api_options: Optional[Dict[str, Any]] = None,
    ):
        self._config = config
        self._rest_api_options = rest_api_options or {}

    @cached_property
    def rest_api(self) -> NetSuiteRestApi:
        return NetSuiteRestApi(self._config, **self._rest_api_options)
    