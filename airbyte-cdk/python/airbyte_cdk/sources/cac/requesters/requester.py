#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Any, Mapping, MutableMapping


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
