import json
import time
import requests
import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class EventsStream(HttpStream):
  primary_key = "id"
  cursor_field = "page"
  page_size = 50000
  url_base = "https://prod-main-net-dashboard-api.azurewebsites.net"
    
  def __init__(self, config: Mapping[str, Any], event_id: str, **_):
    super().__init__()
    self.event_id = event_id
    self.company_id = config["company_id"]
    self._cursor_value = config["page"]

  def request_headers(self, **_) -> Mapping[str, Any]:
    return {}

  def request_params(self, stream_state: Mapping[str, Any], **_) -> MutableMapping[str, Any]:
    return {
      "page": self._cursor_value,
      "eventType": self.event_id,
      "pageSize": self.page_size,
    }

  def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
    lower_response = json.loads(json.dumps(response.json()).lower())
    yield from lower_response

  def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

    if len(response.json()) < self.page_size:
        return None
    else:
      self._cursor_value = self._cursor_value + 1
      return {
        "page": self._cursor_value,
        "eventType": self.event_id,
        "pageSize": self.page_size,
      }

  @property
  def state(self) -> Mapping[str, Any]:
    return {self.cursor_field: self._cursor_value}

  @state.setter
  def state(self, value: Mapping[str, Any]):
    self._cursor_value = self._cursor_value


class MintedEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class PurchasedEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class FullfilledEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class FullfilledErrorEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class RequeuedEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class OpenedEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class PackRevealEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class DepositEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class WithdrawEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class SaleEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class RoyaltyEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


class BurnedNftsEvents(EventsStream):
  def path(self, **_) -> str:
    return f"api/company/{self.company_id}/search"


def str_timestamp_to_str_unix_of_last_value(response):
  latest_timestamp = response[-1]["eventDate"][:25].replace("+", "")
  return str(int(time.mktime(
    datetime.datetime.strptime(
      latest_timestamp, 
      "%Y-%m-%dT%H:%M:%S.%f"
    ).timetuple()
  )))
