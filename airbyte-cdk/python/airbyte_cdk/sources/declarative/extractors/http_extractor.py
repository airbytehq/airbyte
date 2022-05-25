#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.types import Record


class HttpExtractor(ABC):
    @abstractmethod
    def extract_records(self, response: Union[requests.Response, Mapping[str, Any]]) -> List[Record]:
        pass
