#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class CommercetoolsStream(HttpStream, ABC):

    # Page size
    limit = 500
    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"
    filter_field = "lastModifiedAt"
    offset = 0

    def __init__(self, region: str, project_key: str, start_date: str, client_id: str, client_secret: str, host: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.project_key = project_key
        self.region = region
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        total = json_response.get("total", 0)
        offset = json_response.get("offset", 0)
        if offset + self.limit < total:
            return dict(offset=offset + self.limit)
        else:
            return None

    @property
    def url_base(self) -> str:
        return f"https://api.{self.region}.{self.host}.commercetools.com/{self.project_key}/"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"offset": self.offset, "limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        params.update({"sort": "lastModifiedAt asc"})
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get("results", []) if json_response is not None else []
        yield from records


# Basic incremental stream
class IncrementalCommercetoolsStream(CommercetoolsStream, ABC):
    @property
    def limit(self):
        return super().limit

    # Setting the default cursor field for all streams
    cursor_field = "lastModifiedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["limit"] = self.limit
            params["sort"] = "lastModifiedAt asc"
            if stream_state:
                params["where"] = "lastModifiedAt >= :date"
                params["var.date"] = stream_state.get(self.cursor_field)
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


class Customers(IncrementalCommercetoolsStream):
    data_field = "customers"


class DiscountCodes(IncrementalCommercetoolsStream):
    data_field = "discount-codes"


class Orders(IncrementalCommercetoolsStream):
    data_field = "orders"


class Payments(IncrementalCommercetoolsStream):
    data_field = "payments"


class Products(IncrementalCommercetoolsStream):
    data_field = "products"


# Source
class SourceCommercetools(AbstractSource):
    def _convert_auth_to_token(self, username: str, password: str) -> str:
        username = username.encode("latin1")
        password = password.encode("latin1")
        token = b64encode(b":".join((username, password))).strip().decode("ascii")
        return token

    def get_access_token(self, config) -> Tuple[str, any]:
        region = config["region"]
        project_key = config["project_key"]
        host = config["host"]
        url = f"https://auth.{region}.{host}.commercetools.com/oauth/token?grant_type=client_credentials&scope=manage_project:{project_key}"

        try:
            response = requests.post(url, auth=(config["client_id"], config["client_secret"]))
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("access_token", None), None if json_response is not None else None, None
        except requests.exceptions.RequestException as e:
            return None, e

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        region = config["region"]
        project_key = config["project_key"]
        host = config["host"]
        url = f"https://api.{region}.{host}.commercetools.com/{project_key}"
        access_token = self.get_access_token(config)
        token_value = access_token[0]
        token_exception = access_token[1]

        if token_exception:
            return False, token_exception

        if token_value:
            auth = TokenAuthenticator(token=token_value).get_auth_header()
            try:
                response = requests.get(url, headers=auth)
                response.raise_for_status()
                return True, None
            except requests.exceptions.RequestException as e:
                return False, e
        return False, "Token not found"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        access_token = self.get_access_token(config)
        auth = TokenAuthenticator(token=access_token[0])
        args = {
            "authenticator": auth,
            "region": config["region"],
            "host": config["host"],
            "project_key": config["project_key"],
            "start_date": config["start_date"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        }

        return [Customers(**args), Orders(**args), DiscountCodes(**args), Payments(**args), Products(**args)]
