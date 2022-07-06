#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Union

import requests


class Paginator(ABC):
    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        pass

    @abstractmethod
    def path(self) -> Optional[str]:
        pass

    @abstractmethod
    def request_params(self) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_headers(self) -> Mapping[str, Any]:
        pass

    @abstractmethod
    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        pass

    @abstractmethod
    def request_body_json(self) -> Optional[Mapping]:
        pass
