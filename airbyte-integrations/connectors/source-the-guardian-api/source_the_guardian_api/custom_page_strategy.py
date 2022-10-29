from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement

@dataclass
class CustomPageIncrement(PageIncrement):
    """
    Starts page from 1 instead of the default value that is 0.
    """
    def __post_init__(self, options: Mapping[str, Any]):
        self._page = 1

    def reset(self):
        self._page = 1