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


# Basic full refresh stream
class KyribaStream(HttpStream, ABC):
    def __init__(self, base_url: str, version: str, page_size: int, authenticator: TokenAuthenticator):
        super().__init__(authenticator)
        self.base_url = base_url
        self.version = version
        self.page_size = page_size

    primary_key = "uuid"

    @property
    def url_base(self) -> str:
        return f"{self.base_url}/api/v{self.version}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response["metadata"]["links"].get("next")
        next_offset = response["metadata"]["pageOffset"]
        return { "page.offset": next_offset } if next_page else None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response.raise_for_status()
        yield response.json()["results"]


# Basic incremental stream
class IncrementalKyribaStream(KyribaStream, ABC):
    # Checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    # 100 is the default page size
    @property
    def state_checkpoint_interval(self) -> int:
        self.page_size

    cursor_field = "updateDateTime"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_cursor = current_stream_state.get(cursor_field, "")
        latest_cursor = latest_record.get(cursor_field, "")
        return {self.cursor_field: max(current_cursor, latest_cursor)}


class IncrementalKyribaDateTimeStream(IncrementalKyribaStream, ABC):
    cursor_filed = "updateDateTime"


class IncrementalKyribaDateStream(IncrementalKyribaStream, ABC):
    cursor_field = "updateDate"


class Account(KyribaStream):
    def path(self, **kwargs) -> str:
        return "/accounts"


# Source
class SourceKyriba(AbstractSource):
    def base_url(self, config: Mapping[str, Any]) -> str:
        return f"https://{config['subdomain']}.kyriba.com/gateway"

    def get_auth(self, config: Mapping[str, Any], base_url: str) -> TokenAuthenticator:
        username = config["username"]
        password = config["password"]
        url = f"{base_url}/oauth/token"
        data = {"grant_type": "client_credentials"}
        auth = requests.auth.HTTPBasicAuth(username, password)
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
        access_token = response.json()["access_token"]
        return TokenAuthenticator(token=access_token, auth_method="Bearer")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.get_auth(config, self.base_url(config))
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        base_url = self.base_url(config)
        args = {
            "base_url": base_url,
            "version": config["version"],
            "page_size": config["page_size"],
            "authenticator": self.get_auth(config, base_url),
        }
        return [Account(**args)]
