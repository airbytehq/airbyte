#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping


class RequestOptionsProvider(ABC):
    @abstractmethod
    def request_params(self, **kwargs) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_body_data(self, **kwargs) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_body_json(self, **kwargs) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        pass
