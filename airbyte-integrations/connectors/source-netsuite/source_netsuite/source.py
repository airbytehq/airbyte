#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from requests_oauthlib import OAuth1
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime

# Basic full refresh stream
class NetsuiteStream(HttpStream, ABC):
    def __init__(self, auth: OAuth1, name: str, record_url: str, start_date: str = None):
        self.obj_name = name
        self.record_url = record_url
        self.start_date = start_date
        super().__init__(authenticator=auth)

    primary_key = "id"

    @property
    def name(self) -> str:
        return self.obj_name

    @property
    def url_base(self) -> str:
        return self.record_url

    def path(self, **kwargs) -> str:
        return self.obj_name

    def get_json_schema(self, **kwargs) -> dict:
        url = self.url_base + "metadata-catalog/" + self.name
        headers = {"Accept": "application/schema+json"}
        resp = requests.get(url, headers=headers, auth=self._session.auth)
        resp.raise_for_status()
        return resp.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp = response.json()
        offset = resp["offset"]
        count = resp["count"]
        return {"offset": offset + count} if resp["hasMore"] else None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        query = {"q": f"lastModifiedDate GREATER {self.start_date}"} if self.start_date else {}
        return {**query, **next_page_token}

    def fetch_record(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        url = record["links"][0]["href"]
        resp = requests.get(url, auth=self._session.auth)
        resp.raise_for_status()
        return resp.json()

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("items")
        return iter([self.fetch_record(r) for r in records])


# Basic incremental stream
class IncrementalNetsuiteStream(NetsuiteStream, ABC):
    state_checkpoint_interval = 100

    @property
    def cursor_field(self) -> str:
        return "lastModifiedDate"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_cursor = latest_record.get(self.cursor_field) or ""
        current_cursor = current_stream_state.get(self.cursor_field) or ""
        return {self.cursor_field: max(latest_cursor, current_cursor)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        cur = stream_state.get(self.cursor_field) or self.start_date
        query = {"q": f"{self.cursor_field} GREATER {cur}"} if cur else {}
        return {**query, **(next_page_token or {})}

# Source
class SourceNetsuite(AbstractSource):
    def auth(self, config: Mapping[str, Any]) -> OAuth1:
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["token_id"],
            resource_owner_secret=config["token_secret"],
            realm=config["realm"],
            signature_method="HMAC-SHA256",
        )

    def base_url(self, config: Mapping[str, Any]) -> str:
        realm = config["realm"]
        subdomain = realm.lower().replace("_", "-")
        return f"https://{subdomain}.suitetalk.api.netsuite.com/services/rest/"

    def record_url(self, config: Mapping[str, Any]) -> str:
        return self.base_url(config) + "record/v1/"

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = self.base_url(config) + "*"
        auth = self.auth(config)
        requests.options(url, auth=auth).raise_for_status()
        return True, None

    def record_types(self, record_url: str, auth: OAuth1) -> List[str]:
        # get the names of all the record types in an org
        url = record_url + "metadata-catalog"
        records = requests.get(url, auth=auth).json().get("items")
        return [r["name"] for r in records]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        record_url = self.record_url(config)
        auth = self.auth(config)
        start_date = config.get("start_date")
        return [IncrementalNetsuiteStream(auth, name, record_url, start_date) for name in self.record_types(record_url, auth)]
