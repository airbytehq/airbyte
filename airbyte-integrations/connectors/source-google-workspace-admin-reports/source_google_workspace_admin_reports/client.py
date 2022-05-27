#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.sources.deprecated.client import BaseClient

from .api import API, AdminAPI, DriveAPI, IncrementalStreamAPI, LoginsAPI, MeetAPI, MobileAPI, OAuthTokensAPI


class Client(BaseClient):
    def __init__(self, credentials_json: str, email: str, lookback: Optional[int] = None):
        self._api = API(credentials_json, email, lookback)
        self._apis = {
            "admin": AdminAPI(self._api),
            "drive": DriveAPI(self._api),
            "logins": LoginsAPI(self._api),
            "meet": MeetAPI(self._api),
            "mobile": MobileAPI(self._api),
            "oauth_tokens": OAuthTokensAPI(self._api),
        }
        super().__init__()

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return isinstance(self._apis[name], IncrementalStreamAPI)

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            params = {"userKey": "all", "applicationName": "login"}
            self._api.get(name="activities", params=params)
        except Exception as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
