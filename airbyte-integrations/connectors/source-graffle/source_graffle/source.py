import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_events import Events

class SourceGraffle(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, str]:
       return True, "accepted"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Events(config)
        ]
