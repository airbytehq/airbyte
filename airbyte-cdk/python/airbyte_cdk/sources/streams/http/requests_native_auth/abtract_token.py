#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Any, Mapping

from requests.auth import AuthBase


class AbstractHeaderAuthenticator(AuthBase):
    """
    Abstract class for header-based authenticators that set a key-value pair in outgoing HTTP headers
    """

    def __call__(self, request):
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        """HTTP header to set on the requests"""
        return {self.auth_header: self.token}

    @property
    @abstractmethod
    def auth_header(self) -> str:
        """HTTP header to set on the requests"""

    @property
    @abstractmethod
    def token(self) -> str:
        """Value of the HTTP header to set on the requests"""
