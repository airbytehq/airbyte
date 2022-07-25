#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, MutableMapping


class RequestOptionsProvider(ABC):
    @abstractmethod
    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        pass

    @abstractmethod
    def request_body_data(self, **kwargs):
        pass

    @abstractmethod
    def request_body_json(self, **kwargs):
        pass

    @abstractmethod
    def request_kwargs(self, **kwargs):
        pass

    @abstractmethod
    def request_headers(self, **kwargs):
        pass
