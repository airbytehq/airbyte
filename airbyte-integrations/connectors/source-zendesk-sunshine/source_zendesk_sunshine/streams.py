#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import urllib.parse
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class SunshineStream(HttpStream, ABC):
    primary_key = "id"
    data_field = "data"
    page_size = 100

    def __init__(self, subdomain: str, start_date: pendulum.datetime, **kwargs):
        self._start_date = start_date
        self.subdomain = subdomain
        super().__init__(**kwargs)

    @property
    def url_base(self) -> str:
        return f"https://{self.subdomain}.zendesk.com/api/sunshine/"

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return float(delay_time)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if resp_json.get("links") and resp_json.get("links").get("next"):
            next_query_string = urllib.parse.urlsplit(resp_json.get("links").get("next")).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params
        return {}

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        The response data field is mostly a list of objects. Sometimes we can have object in data field.
        (example `ObjectTypePolicies`). In this case this method should be overridden.
        """
        response_json = response.json()
        yield from response_json.get(self.data_field, [])

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalSunshineStream(SunshineStream, ABC):
    state_checkpoint_interval = 1000
    cursor_field = "updated_at"  # most common

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        # dates are ISO-formatted, no need to parse
        return {self.cursor_field: max(latest_state, current_state)}


class ObjectTypes(SunshineStream):
    primary_key = "key"

    def path(self, **kwargs) -> str:
        return "objects/types"


class ObjectRecords(IncrementalSunshineStream):
    """
    The get method supports only the full-refresh way to get the information fron this source.
    This source has date fields in all the endpoints, but we cannot query this field during GET requests.
    To support Incremental for this stream I had to use `query` endpoint instead of `objects/records` -
    this allows me to use date filters. This is the only way to have incremental support.
    """

    http_method = "POST"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        type_ = stream_slice["type"]
        state_value = stream_state.get(type_, {}).get(self.cursor_field)
        start_date = state_value or self._start_date
        formatted_start_date = pendulum.parse(start_date).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        query = {
            "query": {"_type": {"$eq": type_}},
            "_updated_at": {
                "start": formatted_start_date,
            },
            "sort_by": "_updated_at asc",
        }
        return query

    def path(self, **kwargs) -> str:
        return "objects/query"

    def stream_slices(self, **kwargs):
        parent_stream = ObjectTypes(authenticator=self.authenticator, subdomain=self.subdomain, start_date=self._start_date)
        for obj_type in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"type": obj_type["key"]}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        type_ = latest_record.get("type")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_stream_state = current_stream_state or {}
        current_state = current_stream_state.get(type_) if current_stream_state else None
        if current_state:
            current_state = current_state.get(self.cursor_field)
        current_state_value = current_state or latest_cursor_value
        max_value = max(current_state_value, latest_cursor_value)
        new_value = {self.cursor_field: max_value}

        current_stream_state[type_] = new_value
        return current_stream_state


class RelationshipTypes(SunshineStream):
    primary_key = "key"

    def path(self, **kwargs) -> str:
        return "relationships/types"


class RelationshipRecords(SunshineStream):
    def path(self, **kwargs) -> str:
        return "relationships/records"

    def stream_slices(self, **kwargs):
        parent_stream = RelationshipTypes(authenticator=self.authenticator, subdomain=self.subdomain, start_date=self._start_date)
        for rel_type in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"type": rel_type["key"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        type_ = stream_slice["type"]
        params["type"] = type_
        return params


class CustomObjectEvents(SunshineStream):
    """
    This stream is early access stream. (look like a new feature)
    It requires activation in site ui + manual activation from Zendesk via call.
    I requested the call, but since they did not approve it,
    this endpoint will return 403 Forbidden
    """

    def path(self, **kwargs) -> str:
        return "objects/events"


class ObjectTypePolicies(SunshineStream):
    primary_key = None

    def stream_slices(self, **kwargs):
        parent_stream = ObjectTypes(authenticator=self.authenticator, subdomain=self.subdomain, start_date=self._start_date)
        for obj_type in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"type": obj_type["key"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        obj_type = stream_slice["type"]
        return f"objects/types/{obj_type}/permissions"

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        response_json = response.json()
        data = response_json.get(self.data_field, {})
        # the response does not contain info about parent itself - only rules. Need to add this.
        data["object_type"] = stream_slice["type"]
        yield data


class Jobs(SunshineStream):
    """
    This stream is dynamic. The data can exist today, but may be absent tomorrow.
    Since we need to have some data in the stream this stream is disabled.
    """

    def path(self, **kwargs) -> str:
        return "jobs"


class Limits(SunshineStream):
    primary_key = "key"

    def path(self, **kwargs) -> str:
        return "limits"
