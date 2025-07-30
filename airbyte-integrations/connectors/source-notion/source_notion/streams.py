#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging as Logger
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_format


# maximum block hierarchy recursive request depth
MAX_BLOCK_DEPTH = 30


class NotionBackoffStrategy(BackoffStrategy):
    """
    Custom backoff strategy that implements the same logic as the legacy backoff_time method.

    Notion's rate limit is approx. 3 requests per second, with larger bursts allowed.
    For a 429 response, we can use the retry-header to determine how long to wait before retrying.
    For 500-level errors, we use exponential backoff with a retry_factor of 5.
    Docs: https://developers.notion.com/reference/errors#rate-limiting
    """

    def __init__(self, retry_factor: int = 5):
        self.retry_factor = retry_factor

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        if not isinstance(response_or_exception, requests.Response):
            return None

        response = response_or_exception

        # For 429 rate limit errors, use the retry-after header
        if response.status_code == 429:
            retry_after = response.headers.get("retry-after", "5")
            return float(retry_after)

        # For 400 errors with invalid start cursor, return 10 seconds
        if response.status_code == 400:
            message = response.json().get("message", "")
            if message.startswith("The start_cursor provided is invalid: "):
                return 10

        # For 500+ errors, use exponential backoff.
        if response.status_code >= 500:
            backoff_time = self.retry_factor * (2 ** (attempt_count - 1))
            return backoff_time

        # For all other cases, return None to let CDK handle with default behavior
        # This includes 400 errors that don't match our specific case
        return None


class NotionAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Inherit from HttpAvailabilityStrategy with slight modification to 403 error message.
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: Logger, source: Source, error: requests.HTTPError
    ) -> Dict[int, str]:
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

    def __init__(self, config: MutableMapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

        # If start_date is not found in config, set it to 2 years ago and update value in config for use in next stream
        if not self.start_date:
            two_years_ago = datetime.now(timezone.utc) - timedelta(days=730)  # 2 years = 730 days
            self.start_date = self._format_datetime_for_notion(two_years_ago)
            config["start_date"] = self.start_date

    def _format_datetime_for_notion(self, dt) -> str:
        """
        Format datetime for Notion API compatibility.
        Notion expects UTC datetimes in format 'YYYY-MM-DDTHH:MM:SS.000Z' (with 'Z' suffix).
        This maintains backward compatibility with existing state that uses 'Z' format.
        """
        if hasattr(dt, "isoformat"):
            # Convert to UTC if needed and format consistently
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            elif dt.tzinfo != timezone.utc:
                dt = dt.astimezone(timezone.utc)
            # Format with 'Z' suffix for UTC and exactly 3 decimal places for milliseconds
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            # Fallback to standard formatting
            return ab_datetime_format(dt)

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

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        """
        Return custom backoff strategy for Notion API.
        This replaces the deprecated backoff_time method with the modern CDK approach.
        """
        return NotionBackoffStrategy(retry_factor=self.retry_factor)

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

        # Temporary workaround to replace the deprecated calls to super().should_retry(response)
        return response.status_code == 400 or response.status_code == 429 or response.status_code >= 500

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
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # sometimes notion api returns response without results object
        data = response.json().get("results", [])
        yield from data


class IncrementalNotionStream(NotionStream, CheckpointMixin, ABC):
    cursor_field = "last_edited_time"

    http_method = "POST"

    # whether the whole stream sync is finished
    is_finished = True

    def __init__(self, obj_type: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        # object type for search filtering, either "page" or "database" if not None
        self.obj_type = obj_type
        # Track max cursor time across all calls to _get_updated_state
        self._max_cursor_time = ""

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
            return None

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
        # Initialize max cursor time from current state
        self._max_cursor_time = self.state.get(self.cursor_field, "")

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
            if (not stream_state or record_lmd >= state_lmd) and record_lmd >= self.start_date:
                yield record

    def _get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        # Get the current state value as a string
        current_state_value = (current_stream_state or {}).get(self.cursor_field, "")
        record_time = latest_record.get(self.cursor_field, "")

        # Always track the maximum cursor time we've seen
        if record_time:
            if not self._max_cursor_time or record_time > self._max_cursor_time:
                self._max_cursor_time = record_time

        # Only update state when stream sync is finished
        if self.is_finished:
            # When finished, return the maximum cursor time we've tracked
            return {self.cursor_field: self._max_cursor_time}
        else:
            # Keep the current state unchanged when stream is not finished
            return {self.cursor_field: current_state_value}


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
            last_slice = slices[-1]
            if last_slice is not None:
                self.is_finished = page_id == last_slice["parent"]["id"]

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
        for sequence_number, record in enumerate(records):
            if "parent" in record:
                record["parent"]["sequence_number"] = sequence_number
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
                # Temporary workaround to replace the deprecated calls to super().should_retry(response)
                return response.status_code == 429 or response.status_code >= 500
        return response.status_code == 429 or response.status_code >= 500
