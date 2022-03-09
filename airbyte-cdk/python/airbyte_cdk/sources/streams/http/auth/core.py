#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Mapping

from deprecated import deprecated


@deprecated(version="0.1.20", reason="Use requests.auth.AuthBase instead")
class HttpAuthenticator(ABC):
    """
    Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.
    """

    @abstractmethod
    def get_auth_header(self) -> Mapping[str, Any]:
        """
        :return: A dictionary containing all the necessary headers to authenticate.
        """


@deprecated(version="0.1.20", reason="Set `authenticator=None` instead")
class NoAuth(HttpAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {}
