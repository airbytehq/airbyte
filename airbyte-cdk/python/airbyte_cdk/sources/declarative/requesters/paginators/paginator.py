#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.declarative.response import Response


class Paginator(ABC):
    @abstractmethod
    def next_page_token(self, response: Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        pass
