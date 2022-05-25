#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Union

import requests


class Paginator(ABC):
    @abstractmethod
    def next_page_token(
        self, response: Union[requests.Response, Mapping[str, Any]], last_records: List[Mapping[str, Any]]
    ) -> Optional[Mapping[str, Any]]:
        pass
