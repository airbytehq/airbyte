#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import List

import requests
from airbyte_cdk.sources.cac.types import Record


class Extractor(ABC):
    @abstractmethod
    def extract_records(self, response: requests.Response) -> List[Record]:
        pass
