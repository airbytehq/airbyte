#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.response import Response
from airbyte_cdk.sources.declarative.types import Record


class HttpExtractor(ABC):
    @abstractmethod
    def extract_records(self, response: Response) -> Union[List[Record], Mapping[str, Any]]:
        pass

    @abstractmethod
    def get_primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        pass
