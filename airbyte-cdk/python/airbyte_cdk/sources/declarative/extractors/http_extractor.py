#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Union

from airbyte_cdk.sources.declarative.response import Response
from airbyte_cdk.sources.declarative.types import Record


class HttpExtractor(ABC):
    @abstractmethod
    def extract_records(self, response: Response) -> Union[List[Record], Mapping[str, Any]]:
        pass
