#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import b64encode
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class WoocommerceStream(HttpStream, ABC):

    # Latest Stable Release
    api_version = "wc/v3"
    # Page size
    limit = 100
    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"
    order_field = "date"

    def __init__(self, shop: str, start_date: str, api_key: str, api_secret: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.shop = shop
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    def url_base(self) -> str:
        return f"https://{self.shop}.com/wp-json/{self.api_version}/"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        else:
            params.update({"orderby": self.order_field, "order": "asc"})
            params = {"before": datetime.now().isoformat()}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class IncrementalWoocommerceStream(WoocommerceStream, ABC):
    # Getting page size as 'limit' from parrent class
    @property
    def limit(self):
        return super().limit

    # Setting the check point interval to the limit of the records output
    state_checkpoint_interval = limit
    # Setting the default cursor field for all streams
    cursor_field = "date_modified"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if self.cursor_field == "date_modified" and datetime.now().isoformat() < current_stream_state.get(self.cursor_field, ""):
            return {self.cursor_field: latest_record.get(self.cursor_field, "")}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["orderby"] = self.order_field
            params["order"] = "asc"
            if stream_state:
                params["after"] = stream_state.get(self.cursor_field)
        return params

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class NonFilteredStream(IncrementalWoocommerceStream):
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)

        if not next_page_token and stream_state:
            del params["after"]
            del params["before"]
        return params

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:

        slice = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, stream_state=stream_state)
        yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=slice)


class Coupons(IncrementalWoocommerceStream):
    data_field = "coupons"


class Customers(NonFilteredStream):
    data_field = "customers"
    order_field = "registered_date"


class Orders(IncrementalWoocommerceStream):
    data_field = "orders"


# Source
class SourceWoocommerce(AbstractSource):
    def _convert_auth_to_token(self, username: str, password: str) -> str:
        username = username.encode("latin1")
        password = password.encode("latin1")
        token = b64encode(b":".join((username, password))).strip().decode("ascii")
        return token

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.
        """
        shop = config["shop"]
        headers = {"Accept": "application/json"}
        url = f"https://{shop}.com/wp-json/wc/v3/"

        try:
            auth = TokenAuthenticator(token=self._convert_auth_to_token(config["api_key"], config["api_secret"]), auth_method="Basic")
            headers = dict(Accept="application/json", **auth.get_auth_header())
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = auth = TokenAuthenticator(
            token=self._convert_auth_to_token(config["api_key"], config["api_secret"]), auth_method="Basic"
        )  # Oauth2Authenticator is also available if you need oauth support
        args = {
            "authenticator": auth,
            "shop": config["shop"],
            "start_date": config["start_date"],
            "api_key": config["api_key"],
            "api_secret": config["api_secret"],
        }

        return [Customers(**args), Coupons(**args), Orders(**args)]
