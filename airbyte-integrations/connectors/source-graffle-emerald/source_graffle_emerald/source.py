import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_events import (
  CreatedEvents,
  RemovedEvents
)

class SourceGraffleEmerald(AbstractSource):

  def check_connection(self, _, config) -> Tuple[bool, str]:
    event_type = "A.0x39e42c67cc851cfb.EmeraldIdentityDapper.EmeraldIDCreated"
    url_param = f"api/company/{config['company_id']}/search?page=1&eventType={event_type}"
    url = f"https://prod-main-net-dashboard-api.azurewebsites.net/{url_param}"
    response = requests.get(url)
    if len(response.json()) > 0:
      return True, "accepted"
    else:
      return False, "error"

  def streams(self, config: Mapping[str, Any]) -> List[Stream]:
    return [
      CreatedEvents(config, "A.0x39e42c67cc851cfb.EmeraldIdentityDapper.EmeraldIDCreated"),
      RemovedEvents(config, "A.0x39e42c67cc851cfb.EmeraldIdentityDapper.EmeraldIDRemoved")
    ]
