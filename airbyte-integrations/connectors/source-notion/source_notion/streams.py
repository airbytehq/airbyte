#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging as Logger
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, TypeVar

import pendulum
import pydantic
import requests
from requests import HTTPError

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30


class NotionAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Inherit from HttpAvailabilityStrategy with slight modification to 403 error message.
    """

    def reasons_for_unavailable_status_codes(self, stream: Stream, logger: Logger, source: Source, error: HTTPError) -> Dict[int, str]:
        reasons_for_codes: Dict[int, str] = {
            requests.codes.FORBIDDEN: "This is likely due to insufficient permissions for your Notion integration. "
            "Please make sure your integration has read access for the resources you are trying to sync"
        }
        return reasons_for_codes


class NotionStream(HttpStream, ABC):
    url_base = "https://api.notion.com/v1/"

    primary_key = "id"

    page_size = 100  # set by Notion API spec

    raise_on_http_errors = True

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

        # If start_date is not found in config, set it to 2 years ago and update value in config for use in next stream
        if not self.start_date:
            self.start_date = pendulum.now().subtract(years=2).in_timezone("UTC").format("YYYY-MM-DDTHH:mm:ss.SSS[Z]")
            config["start_date"] = self.start_date

    @property
    def availability_strategy(self) -> HttpAvailabilityStrategy:
        return NotionAvailabilityStrategy()

    @property
    def retry_factor(self) -> int:
        return 5

    @property
    def max_retries(self) -> int:
        return 7

    @property
    def max_time(self) -> int:
        return 60 * 11

    @staticmethod
    def check_invalid_start_cursor(response: requests.Response):
        if response.status_code == 400:
            message = response.json().get("message", "")
            if message.startswith("The start_cursor provided is invalid: "):
                return message

    @staticmethod
    def throttle_request_page_size(current_page_size):
        """
        Helper method to halve page_size when encountering a 504 Gateway Timeout error.
        """
        throttled_page_size = max(current_page_size // 2, 10)
        return throttled_page_size

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Notion's rate limit is approx. 3 requests per second, with larger bursts allowed.
        For a 429 response, we can use the retry-header to determine how long to wait before retrying.
        For 500-level errors, we use Airbyte CDK's default exponential backoff with a retry_factor of 5.
        Docs: https://developers.notion.com/reference/errors#rate-limiting
        """
        retry_after = response.headers.get("retry-after", "5")
        if response.status_code == 429:
            return float(retry_after)
        if self.check_invalid_start_cursor(response):
            return 10
        return super().backoff_time(response)

    def should_retry(self, response: requests.Response) -> bool:
        # In the case of a 504 Gateway Timeout error, we can lower the page_size when retrying to reduce the load on the server.
        if response.status_code == 504:
            self.page_size = self.throttle_request_page_size(self.page_size)
            self.logger.info(f"Encountered a server timeout. Reducing request page size to {self.page_size} and retrying.")

        # If page_size has been reduced after encountering a 504 Gateway Timeout error,
        # we increase it back to the default of 100 once a success response is achieved, for the following API calls.
        if response.status_code == 200 and self.page_size != 100:
            self.page_size = 100
            self.logger.info(f"Successfully reconnected after a server timeout. Increasing request page size to {self.page_size}.")

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
        Doc: https://developers.notion.com/reference/intro#pagination
        """
        next_cursor = response.json().get("next_cursor")
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
    max_cursor_time: Any = ""

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


class IncrementalNotionStream(NotionStream, CheckpointMixin, ABC):
    cursor_field = "last_edited_time"

    http_method = "POST"

    # whether the whole stream sync is finished
    is_finished = True

    def __init__(self, obj_type: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        # object type for search filtering, either "page" or "database" if not None
        self.obj_type = obj_type

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

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

        self.state = stream_state or {}

        try:
            for record in super().read_records(sync_mode, stream_state=stream_state, **kwargs):
                self.state = self._get_updated_state(self.state, record)
                yield record
        except UserDefinedBackoffException as e:
            message = self.check_invalid_start_cursor(e.response)
            if message:
                self.logger.error(f"Skipping stream {self.name}, error message: {message}")
                return
            raise e

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        records = super().parse_response(response, stream_state=stream_state, **kwargs)
        for record in records:
            record_lmd = record.get(self.cursor_field, "")
            state_lmd = stream_state.get(self.cursor_field, "")
            if isinstance(state_lmd, StateValueWrapper):
                state_lmd = state_lmd.value
            if (not stream_state or record_lmd >= state_lmd) and record_lmd >= self.start_date:
                yield record

    def _get_updated_state(
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

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        transform_object_field = record.get("type")

        if transform_object_field:
            rich_text = record.get(transform_object_field, {}).get("rich_text", [])
            for r in rich_text:
                mention = r.get("mention")
                if mention:
                    type_info = mention[mention["type"]]
                    record[transform_object_field]["rich_text"][rich_text.index(r)]["mention"]["info"] = type_info
                    del record[transform_object_field]["rich_text"][rich_text.index(r)]["mention"][mention["type"]]

        return record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        # pages and databases blocks are already fetched in their streams, so no
        # need to do it again
        # fetching of `ai_block` type is unsupported by API
        # https://github.com/airbytehq/oncall/issues/1927
        records = super().parse_response(response, stream_state=stream_state, **kwargs)
        for record in records:
            if record["type"] not in ("child_page", "child_database", "ai_block"):
                yield self.transform(record)

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        # if reached recursive limit, don't read anymore
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
