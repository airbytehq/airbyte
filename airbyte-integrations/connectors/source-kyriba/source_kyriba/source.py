#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

class KyribaClient:
    def __init__(self, username: str, password: str, gateway_url: str):
        self.username = username
        self.password = password
        self.url = f"{gateway_url}/oauth/token"

    def login(self) -> TokenAuthenticator:
        data = {"grant_type": "client_credentials"}
        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        response = requests.post(self.url, auth=auth, data=data)
        response.raise_for_status()
        access_token = response.json()["access_token"]
        return TokenAuthenticator(access_token)

# Basic full refresh stream
class KyribaStream(HttpStream):
    def __init__(
            self,
            gateway_url: str,
            client: KyribaClient,
            version: str = 1,
            start_date: str = None,
    ):
        self.gateway_url = gateway_url
        self.version = version
        self.start_date = start_date
        self.client = client
        super().__init__(self.client.login())

    primary_key = "uuid"

    @property
    def url_base(self) -> str:
        return f"{self.gateway_url}/api/v{self.version}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        metadata = response.json()["metadata"]
        next_page = metadata["links"].get("next")
        next_offset = metadata["pageOffset"] + metadata["pageLimit"]
        return { "page.offset": next_offset } if next_page else None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def should_retry(self, response: requests.Response) -> bool:
        # Kyriba uses basic auth to generate an expiring bearer token
        # There is no refresh token, so users need to log in again when the token expires
        if response.status_code == 401:
            self._authorization = self.client.login()
            return True
        return response.status_code == 429 or 500 <= response.status_code < 600

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("results")


# Basic incremental stream
class IncrementalKyribaStream(KyribaStream, ABC):
    cursor_field = "updateDateTime"

    # Checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    @property
    def state_checkpoint_interval(self) -> int:
        # 100 is the default page size
        return 100

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_cursor = latest_record.get(self.cursor_field) or ""
        current_cursor = current_stream_state.get(self.cursor_field) or ""
        return {self.cursor_field: max(current_cursor, latest_cursor)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = { "sort": self.cursor_field }
        latest_cursor = stream_state.get(self.cursor_field) or self.start_date + " 00:00:00"
        if latest_cursor:
            # the Kyriba datetime output contains T and Z, but the input has a space and no time zone
            fmt_cursor = latest_cursor.replace("T", " ").replace("Z", "")
            filter = f"{self.cursor_field}=gt='{fmt_cursor}'"
            params["filter"] = filter
        if next_page_token:
            params = {**params, **next_page_token}
        return params


class Accounts(KyribaStream):
    def path(self, **kwargs) -> str:
        return "accounts"


class CashFlows(IncrementalKyribaStream):
    def path(self, **kwargs) -> str:
        return "cash-flows"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # the updateDateTime is nested, so we need to adap this method
        latest_cursor = latest_record["date"].get(self.cursor_field) or ""
        current_cursor = current_stream_state.get(self.cursor_field) or ""
        return {self.cursor_field: max(current_cursor, latest_cursor)}

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs) or {}
        params["dateType"] = "UPDATE"
        params["start_date"] = self.start_date
        return params


# Source
class SourceKyriba(AbstractSource):
    def gateway_url(self, config: Mapping[str, Any]) -> str:
        return f"https://{config['domain']}/gateway"

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        client = KyribaClient(config["username"], config["password"], self.gateway_url(config))
        client.login()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        gateway_url = self.gateway_url(config)
        client = KyribaClient(config["username"], config["password"], gateway_url)
        kwargs = {
            "gateway_url": gateway_url,
            "version": config.get("version"),
            "client": client,
            "start_date": config.get("start_date"),
        }
        return [Accounts(**kwargs), CashFlows(**kwargs)]
