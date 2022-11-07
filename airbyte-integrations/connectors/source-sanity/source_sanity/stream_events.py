import json
import requests
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class EventsStream(HttpStream):
  primary_key = "id"
  url_base = ""
    
  def __init__(self, config: Mapping[str, Any], query: str, **_):
    super().__init__()
    self.url_base = config["host"]
    self.api_key = config["api_key"]
    self.query = query

  def request_headers(self, **_) -> Mapping[str, Any]:
    return {
      "Authorization": f"Bearer {self.api_key}"
    }

  def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
    response_json = response.json()
    yield from response.json()["result"]

  def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
    return None


class Challenges(EventsStream):
  def path(self, **_) -> str:
    return "v2021-06-07/data/query/production"
  def request_params(self, **_) -> MutableMapping[str, Any]:
    return {"query": self.query}
