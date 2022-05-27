#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import List

from airbyte_cdk.sources.declarative.response import Response
from airbyte_cdk.sources.declarative.types import Record


class HttpExtractor(ABC):
    @abstractmethod
    def extract_records(self, response: Response) -> List[Record]:
        pass
