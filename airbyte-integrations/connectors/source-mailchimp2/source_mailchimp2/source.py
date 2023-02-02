import json
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    Status,
)
from airbyte_cdk.sources import Source

from .stream import (
    Campaigns
)

class SourceMailchimp2(Source):
    def check(self, logger: AirbyteLogger, config: json) -> Tuple[bool, str]:
       return True, "accepted"
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Campaigns(config),
        ]
