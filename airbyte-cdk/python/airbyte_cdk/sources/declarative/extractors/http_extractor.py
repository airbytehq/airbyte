#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import List

import requests
from airbyte_cdk.sources.declarative.types import Record


class HttpExtractor(ABC):
    @abstractmethod
    def extract_records(self, response: requests.Response) -> List[Record]:
        pass
