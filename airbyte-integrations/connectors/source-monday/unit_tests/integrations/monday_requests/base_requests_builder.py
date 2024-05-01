# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import abc
from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest

from .request_authenticators.authenticator import Authenticator


class MondayRequestBuilder(abc.ABC):
    @property
    @abc.abstractmethod
    def url(self) -> str:
        """A url"""

    @property
    @abc.abstractmethod
    def query_params(self) -> Dict[str, Any]:
        """Query params"""

    @property
    @abc.abstractmethod
    def headers(self) -> Dict[str, Any]:
        """Headers"""

    @property
    @abc.abstractmethod
    def request_body(self) -> Optional[str]:
        """A request body"""

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=self.url,
            query_params=self.query_params,
            headers=self.headers,
            body=self.request_body
        )


class MondayBaseRequestBuilder(MondayRequestBuilder):
    def __init__(self, resource: str = "") -> None:
        self._resource: str = resource
        self._authenticator: str = None

    @property
    def url(self) -> str:
        return f"https://api.monday.com/v2/{self._resource}"

    @property
    def headers(self) -> Dict[str, Any]:
        return (super().headers or {}) | {
            "Authorization": self._authenticator.client_access_token,
        }

    @property
    def request_body(self):
        return super().request_body

    def with_authenticator(self, authenticator: Authenticator) -> "MondayBaseRequestBuilder":
        self._authenticator: Authenticator = authenticator
        return self
