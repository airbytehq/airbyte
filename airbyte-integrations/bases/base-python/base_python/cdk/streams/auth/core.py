#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Mapping


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


class NoAuth(HttpAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {}
