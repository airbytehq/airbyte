#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.types import Record


class HttpSelector(ABC):
    @abstractmethod
    def select_records(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> List[Record]:
        pass
