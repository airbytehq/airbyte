from abc import ABC, abstractmethod
from typing import Any

from foundry._core.auth_utils import Auth
from foundry.api_client import ApiClient, RequestInfo


class FoundryService(ABC):
    @abstractmethod
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        pass


class FoundryApiClient:
    def __init__(self, host: str, api_auth: Auth, service_name: str) -> None:
        self.api_client = ApiClient(
            auth=api_auth,
            # ApiClient automatically makes requests to "https://<hostname>/api" so must include service in hostname
            hostname=f"{host}/{service_name}"
        )

    def call_api(self, request_info: RequestInfo) -> Any:
        return self.api_client.call_api(request_info)
