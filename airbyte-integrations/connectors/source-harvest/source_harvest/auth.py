from typing import Mapping, Any

from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class HarvestTokenAuthenticator(HttpAuthenticator):
    def __init__(
        self,
        token: str,
        account_id: str,
        auth_method: str = "Bearer",
        auth_header: str = "Authorization",
        account_id_header: str = "Harvest-Account-ID"
    ):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._token = token
        self.account_id = account_id
        self.account_id_header = account_id_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {
            self.auth_header: f"{self.auth_method} {self._token}",
            self.account_id_header: self.account_id
        }
