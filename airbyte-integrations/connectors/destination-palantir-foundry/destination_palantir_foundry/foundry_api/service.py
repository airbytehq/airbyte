from destination_palantir_foundry.config.foundry_config import FoundryConfig
from foundry.api_client import ApiClient, RequestInfo
from foundry._core.auth_utils import Auth
from typing import Any


class FoundryService:  # TODO(jcrowson): remove config here and just pass host
    def __init__(self, host: str, api_auth: Auth, service_name: str) -> None:
        self.api_client = ApiClient(
            auth=api_auth,
            # ApiClient automatically makes requests to "https://<hostname>/api" so must include service in hostname
            hostname=f"{host}/{service_name}"
        )

    def call_api(self, request_info: RequestInfo) -> Any:
        return self.api_client.call_api(request_info)
