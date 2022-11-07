import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import AbstractSource

from .stream_events import (
  Challenges
)


class SourceSanity(AbstractSource):

  def check_connection(self, _, config) -> Tuple[bool, str]:
    response = requests.get(
        config['host'],
        params={"query": "*[_id == 'termsPage'][0]"},
        headers={"Authorization": f"Bearer {config['api_key']}"}
    )
    if response.status_code == 200:
      return True, "accepted"
    else:
      return False, "rejected"

  def streams(self, config: Mapping[str, Any]) -> List[Stream]:
    return [
      Challenges(config, "*[_type == 'challenge']")
    ]
