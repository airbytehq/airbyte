import json
import requests
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class EventsStream(HttpStream):
  primary_key = "id"
  url_base = ""
    
  def __init__(self, config: Mapping[str, Any], collection: str, **_):
    super().__init__()
    self.url_base = config["host"]
    self.api_key = config["api_key"]
    self.collection = collection

  def request_headers(self, **_) -> Mapping[str, Any]:
    return {
      "X-TYPESENSE-API-KEY": self.api_key
    }

  def request_params(self, **_) -> MutableMapping[str, Any]:
    return {}

  def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
    output = []
    for exported_doc_str in response.text.split('\n'):
      output.append(json.loads(exported_doc_str))
    yield from output

  def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
    return None


class Moments(EventsStream):
  def path(self, **_) -> str:
    return f"collections/{self.collection}/documents/export"


class Market(EventsStream):
  def path(self, **_) -> str:
    return f"collections/{self.collection}/documents/export"
