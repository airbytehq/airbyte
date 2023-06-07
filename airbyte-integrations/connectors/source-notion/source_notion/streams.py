#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, TypeVar

import pydantic
import requests
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from airbyte_cdk.utils import AirbyteTracedException

from .utils import transform_properties

# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30


class NotionStream(HttpStream, ABC):

    url_base = "https://api.notion.com/v1/"

    primary_key = "id"

    page_size = 100  # set by Notion API spec

    raise_on_http_errors = True

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = config["start_date"]

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def check_invalid_start_cursor(self, response: requests.Response):
        if response.status_code == 400:
            message = response.json().get("message", "")
            if message.startswith("The start_cursor provided is invalid: "):
                return message

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            return float(retry_after)
        if self.check_invalid_start_cursor(response):
            return 10

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 400 or super().should_retry(response)

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        params = super().request_headers(**kwargs)
        # Notion API version, see https://developers.notion.com/reference/versioning
        params["Notion-Version"] = "2022-06-28"
        return params

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        """
        An example of response:
        {
            "next_cursor": "fe2cc560-036c-44cd-90e8-294d5a74cebc",
            "has_more": true,
            "results": [ ... ]
        }
        Doc: https://developers.notion.com/reference/pagination
        """
        next_cursor = response.json()["next_cursor"]
        if next_cursor:
            return {"next_cursor": next_cursor}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # sometimes notion api returns response without results object
        data = response.json().get("results", [])
        yield from data


T = TypeVar("T")


class StateValueWrapper(pydantic.BaseModel):

    stream: T
    state_value: str
    max_cursor_time = ""

    def __repr__(self):
        """Overrides print view"""
        return self.value

    @property
    def value(self) -> str:
        """Return max cursor time after stream sync is finished."""
        return self.max_cursor_time if self.stream.is_finished else self.state_value

    def dict(self, **kwargs):
        """Overrides default logic to return current value only."""
        return {pydantic.utils.ROOT_KEY: self.value}


class IncrementalNotionStream(NotionStream, ABC):

    cursor_field = "last_edited_time"

    http_method = "POST"

    # whether the whole stream sync is finished
    is_finished = True

    def __init__(self, obj_type: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        # object type for search filtering, either "page" or "database" if not None
        self.obj_type = obj_type

    def path(self, **kwargs) -> str:
        return "search"

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        if not self.obj_type:
            return

        # search request body
        # Docs: https://developers.notion.com/reference/post-search
        body = {
            "sort": {"direction": "ascending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": self.obj_type},
            "page_size": self.page_size,
        }
        if next_page_token:
            body["start_cursor"] = next_page_token["next_cursor"]

        return body

    def read_records(self, sync_mode: SyncMode, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        if sync_mode == SyncMode.full_refresh:
            stream_state = None
        try:
            yield from super().read_records(sync_mode, stream_state=stream_state, **kwargs)
        except UserDefinedBackoffException as e:
            message = self.check_invalid_start_cursor(e.response)
            if message:
                raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)
            raise e

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        records = super().parse_response(response, stream_state=stream_state, **kwargs)
        for record in records:
            record_lmd = record.get(self.cursor_field, "")
            state_lmd = stream_state.get(self.cursor_field, "")
            if isinstance(state_lmd, StateValueWrapper):
                state_lmd = state_lmd.value
            if not stream_state or record_lmd >= state_lmd:
                yield from transform_properties(record)

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        state_value = (current_stream_state or {}).get(self.cursor_field, "")
        if not isinstance(state_value, StateValueWrapper):
            state_value = StateValueWrapper(stream=self, state_value=state_value)

        record_time = latest_record.get(self.cursor_field, self.start_date)
        state_value.max_cursor_time = max(state_value.max_cursor_time, record_time)

        return {self.cursor_field: state_value}


class Users(NotionStream):
    """
    Docs: https://developers.notion.com/reference/get-users
    """

    def path(self, **kwargs) -> str:
        return "users"

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if next_page_token:
            params["start_cursor"] = next_page_token["next_cursor"]
        return params


class Databases(IncrementalNotionStream):
    """
    Docs: https://developers.notion.com/reference/post-search
    """

    state_checkpoint_interval = 100

    def __init__(self, **kwargs):
        super().__init__(obj_type="database", **kwargs)


class Pages(IncrementalNotionStream):
    """
    Docs: https://developers.notion.com/reference/post-search
    """

    state_checkpoint_interval = 100

    def __init__(self, **kwargs):
        super().__init__(obj_type="page", **kwargs)


class Blocks(HttpSubStream, IncrementalNotionStream):
    """
    Docs: https://developers.notion.com/reference/get-block-children
    """

    http_method = "GET"

    # block id stack for block hierarchy traversal
    block_id_stack = []

    def path(self, **kwargs) -> str:
        return f"blocks/{self.block_id_stack[-1]}/children"

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if next_page_token:
            params["start_cursor"] = next_page_token["next_cursor"]
        return params

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # gather parent stream records in full
        slices = list(super().stream_slices(SyncMode.full_refresh, cursor_field, stream_state))

        self.is_finished = False
        for page in slices:
            page_id = page["parent"]["id"]
            self.block_id_stack.append(page_id)

            # stream sync is finished when it is on the last slice
            self.is_finished = page_id == slices[-1]["parent"]["id"]

            yield {"page_id": page_id}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        # pages and databases blocks are already fetched in their streams, so no
        # need to do it again
        # fetching of `ai_block` type is unsupported by API
        # https://github.com/airbytehq/oncall/issues/1927
        records = super().parse_response(response, stream_state=stream_state, **kwargs)
        for record in records:
            if record["type"] not in ("child_page", "child_database", "ai_block"):
                yield record

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        # if reached recursive limit, don't read any more
        if len(self.block_id_stack) > MAX_BLOCK_DEPTH:
            return

        records = super().read_records(**kwargs)
        for record in records:
            if record.get("has_children", False):
                # do the depth first traversal recursive call, get children blocks
                self.block_id_stack.append(record["id"])
                yield from self.read_records(**kwargs)
            yield record

        self.block_id_stack.pop()

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 404:
            setattr(self, "raise_on_http_errors", False)
            self.logger.error(
                f"Stream {self.name}: {response.json().get('message')}. 404 HTTP response returns if the block specified by id doesn't"
                " exist, or if the integration doesn't have access to the block."
                "See more in docs: https://developers.notion.com/reference/get-block-children"
            )
            return False

        if response.status_code == 400:
            error_code = response.json().get("code")
            error_msg = response.json().get("message")
            if "validation_error" in error_code and "ai_block is not supported" in error_msg:
                setattr(self, "raise_on_http_errors", False)
                self.logger.error(
                    f"Stream {self.name}: `ai_block` type is not supported, skipping. See https://developers.notion.com/reference/block for available block type."
                )
                return False
            else:
                return super().should_retry(response)
        return super().should_retry(response)
