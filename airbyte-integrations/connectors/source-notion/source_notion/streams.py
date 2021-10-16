import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

# maximum block recursive hierarchy depth
MAX_BLOCK_DEPTH = 30


class NotionStream(HttpStream, ABC):

    url_base = "https://api.notion.com/v1/"

    primary_key = "id"

    page_size = 100     # set by Notion API

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = config["start_date"]

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        params = super().request_headers(stream_state, stream_slice, next_page_token)
        # Notion API version, see https://developers.notion.com/reference/versioning
        params["Notion-Version"] = "2021-08-16"
        return params

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        next_cursor = response.json()["next_cursor"]
        if next_cursor:
            return { "next_cursor": next_cursor }

    # default record filter, do nothing
    def filter_by_state(
        self,
        stream_state: Mapping[str, Any] = None,
        record: Mapping[str, Any] = None
    ) -> Iterable:
        yield record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json().get("results")
        for record in data:
            yield from self.filter_by_state(stream_state=stream_state, record=record)


class IncrementalNotionStream(NotionStream, ABC):

    cursor_field = "last_edited_time"

    http_method = "POST"

    def __init__(self, obj_type: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.obj_type = obj_type
        self.filter_on = True

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "search"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        if not self.obj_type:
            return

        body = {
            "sort": { "direction": "ascending", "timestamp": "last_edited_time" },
            "filter": { "property": "object", "value": self.obj_type },
            "page_size": self.page_size
        }
        if next_page_token:
            body["start_cursor"] = next_page_token["next_cursor"]

        return body

    def filter_by_state(
        self,
        stream_state: Mapping[str, Any] = None,
        record: Mapping[str, Any] = None
    ) -> Iterable:
        if not self.filter_on:
            yield record
            return

        value = ""
        if record:
            value = record.get(self.cursor_field, value)
        if not stream_state or value >= stream_state.get(self.cursor_field, ""):
            yield record

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        state_date = current_stream_state.get(self.cursor_field, self.start_date)
        record_date = latest_record.get(self.cursor_field, self.start_date)
        return { self.cursor_field: max(state_date, record_date) }


class Users(NotionStream):

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "users"


class Databases(IncrementalNotionStream):

    def __init__(self, **kwargs):
        super().__init__(obj_type = "database", **kwargs)


class Pages(IncrementalNotionStream):

    def __init__(self, **kwargs):
        super().__init__(obj_type = "page", **kwargs)


class Blocks(HttpSubStream, IncrementalNotionStream):

    http_method = "GET"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # block id stack for block hierarchy traversal
        self.block_id_stack = []

        # largest time in cursor field across all stream slices
        self.max_cursor_time = self.start_date

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"blocks/{self.block_id_stack[-1]}/children"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = { "page_size": self.page_size }
        if next_page_token:
            params["start_cursor"] = next_page_token["next_cursor"]
        return params

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # turn off parent's record filter to get full list of parents, because
        # children's changed time may not propagated to parent
        self.parent.filter_on = False

        parents = super().stream_slices(sync_mode, cursor_field, stream_state)
        for item in parents:
            parent_id = item["parent"]["id"]
            self.block_id_stack.append(parent_id)
            yield { "page_id": parent_id }
        yield from []

    def filter_by_state(
        self,
        stream_state: Mapping[str, Any] = None,
        record: Mapping[str, Any] = None
    ) -> Iterable:
        # pages and databases blocks are already fetched in their streams, no
        # need to do it again
        for item in super().filter_by_state(stream_state, record):
            if item["type"] not in ("child_page", "child_database"):
                yield item

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # if reached recursive limit, don't read any more
        if len(self.block_id_stack) > MAX_BLOCK_DEPTH:
            yield from []
            return

        records =  super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        for record in records:
            if record["has_children"]:
                self.block_id_stack.append(record["id"])
                yield from self.read_records(sync_mode, cursor_field, stream_slice, stream_state)
            else:
                yield record

        self.block_id_stack.pop()

        yield from []

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        # we don't update state here, just keep a record of maximum cursor field
        # date, state will be actually updated after syncing the whole stream
        record_date = latest_record.get(self.cursor_field, self.start_date)
        self.max_cursor_time = max(self.max_cursor_time, record_date)
        return current_stream_state

