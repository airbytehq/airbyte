#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Any, Mapping

from requests.auth import AuthBase


class AbstractHeaderAuthenticator(AuthBase):
    """Abstract class for an header-based authenticators that add a header to outgoing HTTP requests."""

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""
        return {self.auth_header: self.token}

    @property
    @abstractmethod
    def auth_header(self) -> str:
        """The header key to set on outgoing HTTP requests"""

    @property
    @abstractmethod
    def token(self) -> str:
        """The header value to set on outgoing HTTP requests"""
