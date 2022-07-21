#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Any, Mapping

from requests.auth import AuthBase


class AbstractHeaderAuthenticator(AuthBase):
    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: self.token}

    @property
    @abstractmethod
    def auth_header(self) -> str:
        pass

    @property
    @abstractmethod
    def token(self) -> str:
        pass
