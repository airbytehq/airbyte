#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Any, Mapping, MutableMapping, Optional

import requests


class Requester(ABC):
    @abstractmethod
    def get_authenticator(self):
        pass

    @abstractmethod
    def get_url_base(self):
        pass

    @abstractmethod
    def get_path(self):
        pass

    @abstractmethod
    def get_method(self):
        pass

    @abstractmethod
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        pass

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
