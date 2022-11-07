from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import AbstractSource

from .stream_events import (
  Moments,
  Market
)


class SourceTypesense(AbstractSource):

  def check_connection(self, _, config) -> Tuple[bool, str]:
      return True, "accepted"

  def streams(self, config: Mapping[str, Any]) -> List[Stream]:
    return [
      Moments(config, "moments"),
      Market(config, "market")
    ]
