#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import binascii
import struct
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib import parse

import requests

from airbyte_cdk import BackoffStrategy, StreamSlice
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.checkpoint.substream_resumable_full_refresh_cursor import SubstreamResumableFullRefreshCursor
from airbyte_cdk.sources.streams.core import CheckpointMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.utils import AirbyteTracedException

from . import constants
from .backoff_strategies import GithubStreamABCBackoffStrategy
from .errors_handlers import (
    GITHUB_DEFAULT_ERROR_MAPPING,
    GithubStreamABCErrorHandler,
    is_conflict_with_empty_repository,
    is_gone_with_feature_disabled,
)
from .utils import getter


class GithubStreamABC(HttpStream, ABC):
    primary_key = "id"

    # Detect streams with high API load
    large_stream = False
    max_retries: int = 5
    stream_base_params = {}

    def __init__(
        self,
        api_url: str = "https://api.github.com",
        access_token_type: str = "",
        max_wait_time_seconds: float = 120 * 60,
        **kwargs,
    ):
        self.max_wait_time_seconds = max_wait_time_seconds
        super().__init__(**kwargs)

        self.access_token_type = access_token_type
        self.api_url = api_url
        self.state = {}

        if not self.supports_incremental:
            self.cursor = SubstreamResumableFullRefreshCursor()

    @property
    def url_base(self) -> str:
        return self.api_url

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        links = response.links
        if "next" in links:
            next_link = links["next"]["url"]
            parsed_link = parse.urlparse(next_link)
            page = dict(parse.parse_qsl(parsed_link.query)).get("page")
            return {"page": page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.page_size}

        if next_page_token:
            params.update(next_page_token)

        params.update(self.stream_base_params)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        # Without sending `User-Agent` header we will be getting `403 Client Error: Forbidden for url` error.
        return {"User-Agent": "PostmanRuntime/7.28.0"}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for record in response.json():  # GitHub puts records in an array.
            yield self.transform(record=record, stream_slice=stream_slice)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return GithubStreamABCErrorHandler(
            logger=self.logger, max_retries=self.max_retries, error_mapping=GITHUB_DEFAULT_ERROR_MAPPING, stream=self
        )

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return GithubStreamABCBackoffStrategy(stream=self, max_wait_time_seconds=self.max_wait_time_seconds)

    @staticmethod
    def check_graphql_rate_limited(response_json: dict) -> bool:
        errors = response_json.get("errors")
        if errors:
            for error in errors:
                if error.get("type") == "RATE_LIMITED":
                    return True
        return False

    def read_records(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        repository = stream_slice.get("repository", "")
        # Reading records while handling the errors
        try:
            yield from super().read_records(stream_slice=stream_slice, **kwargs)
        # HTTP Client wraps DefaultBackoffException into AirbyteTracedException
        except AirbyteTracedException as e:
            # This whole try/except situation in `read_records()` isn't good but right now in `self._send_request()`
            # function we have `response.raise_for_status()` so we don't have much choice on how to handle errors.
            # Bocked on https://github.com/airbytehq/airbyte/issues/3514.
            # `requests.RequestException` subclasses always expose a `response` attribute, but it
            # defaults to `None` for transport-layer failures (ConnectionError, ConnectTimeout,
            # ReadTimeout, SSLError, DNS failures, etc.). Treat a missing or `None` response as
            # something this handler cannot classify, and let the CDK surface it.
            if not hasattr(e, "_exception") or getattr(e._exception, "response", None) is None:
                raise e
            if e._exception.response.status_code == requests.codes.NOT_FOUND:
                error_msg = (
                    f"Skipping `{self.__class__.__name__}` for repository `{repository}`: "
                    f"GitHub returned 404 Not Found. The repository may not exist, may have been deleted, "
                    f"or the configured token may lack access to it."
                )
            elif e._exception.response.status_code == requests.codes.FORBIDDEN:
                api_message = (e._exception.response.json() or {}).get("message", "")
                error_msg = (
                    f"Skipping `{self.name}` for repository `{repository}`: "
                    f"GitHub denied access (HTTP 403). Your token may be missing required scopes, "
                    f"or this organization may require SAML SSO authorization. "
                    f"GitHub message: {api_message!r}"
                )
            elif e._exception.response.status_code == requests.codes.UNAUTHORIZED:
                api_message = (e._exception.response.json() or {}).get("message", "")
                if self.access_token_type == constants.PERSONAL_ACCESS_TOKEN_TITLE:
                    self.logger.error(
                        f"GitHub authentication failed (HTTP 401) for stream `{self.name}`. "
                        f"Your Personal Access Token may need to be renewed. GitHub message: {api_message!r}"
                    )
                raise e

            elif e._exception.response.status_code == requests.codes.CONFLICT:
                error_msg = (
                    f"Skipping `{self.name}` for repository `{stream_slice['repository']}`: "
                    f"GitHub returned 409 Conflict. The repository is likely empty (no commits)."
                )
            elif e._exception.response.status_code == requests.codes.BAD_GATEWAY:
                error_msg = (
                    f"GitHub returned HTTP 502 Bad Gateway for stream `{self.name}` after exhausting retries. "
                    f"This is usually transient — the next sync attempt should succeed."
                )
            elif e._exception.response.status_code == requests.codes.GATEWAY_TIMEOUT:
                error_msg = (
                    f"GitHub returned HTTP 504 Gateway Timeout for stream `{self.name}` after exhausting retries "
                    f"and reducing the GraphQL page size. The next sync attempt should succeed; "
                    f'if 504s persist, lower "Page size for large streams" in the source configuration.'
                )
            else:
                self.logger.error(f"Undefined error while reading records: {e._exception.response.text}")
                raise e

            self.logger.warning(error_msg)
            self._close_slice_after_swallowed_error(stream_slice)
        # Exhausting every token no longer raises a connector-specific exception here: the
        # shared authenticator raises AirbyteTracedException(transient_error) itself, which the
        # `except AirbyteTracedException` branch above re-raises untouched (it carries no
        # response to classify).

    def _close_slice_after_swallowed_error(self, stream_slice: Optional[Mapping[str, Any]]) -> None:
        """Mark the slice complete when `read_records` skipped it instead of raising.

        `HttpStream._read_pages` closes a resumable-full-refresh slice only after the last
        page, so an error swallowed mid-slice leaves the partition's cursor state empty and
        `CursorBasedCheckpointReader._find_next_slice` hands the same partition back forever
        — no record, no STATE, and the platform kills the attempt on the source heartbeat.
        Closing the slice makes a swallowed error terminal, as the warning above implies.
        """
        cursor = self.get_cursor()
        if not isinstance(cursor, SubstreamResumableFullRefreshCursor):
            return
        # Only close a partition the slice actually names. Several substreams read their parent
        # by calling its `read_records` straight from `stream_slices()` with a bare mapping that
        # has no `partition` key (`TeamMembers`, `IssueTimelineEvents`, `utils.read_full_refresh`,
        # ...), and those parents are shared instances that emit their own STATE later — closing
        # `_extract_slice_fields`' `{}` fallback would put a meaningless entry in it.
        partition = (stream_slice or {}).get("partition")
        if not partition:
            return
        cursor.close_slice(StreamSlice(cursor_slice={}, partition=partition))


class GithubStream(GithubStreamABC):
    def __init__(self, repositories: List[str], page_size_for_large_streams: int, **kwargs):
        super().__init__(**kwargs)
        self.repositories = repositories
        # GitHub pagination could be from 1 to 100.
        # This parameter is deprecated and in future will be used sane default, page_size: 10
        self.page_size = page_size_for_large_streams if self.large_stream else constants.DEFAULT_PAGE_SIZE

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"repos/{stream_slice['repository']}/{self.name}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for repository in self.repositories:
            yield {"repository": repository}

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        if (
            isinstance(exception, DefaultBackoffException)
            and exception.response.status_code in (requests.codes.BAD_GATEWAY, requests.codes.GATEWAY_TIMEOUT)
            and self.large_stream
            and self.page_size > 1
        ):
            return (
                f'Please try to decrease the "Page size for large streams" below {self.page_size}. '
                f'The stream "{self.name}" is a large stream, such streams can fail with '
                f'{exception.response.status_code} for high "page_size" values.'
            )
        return super().get_error_display_message(exception)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any]) -> MutableMapping[str, Any]:
        record["repository"] = stream_slice["repository"]

        if "reactions" in record and record["reactions"]:
            reactions = record["reactions"]
            if "+1" in reactions:
                reactions["plus_one"] = reactions.pop("+1")
            if "-1" in reactions:
                reactions["minus_one"] = reactions.pop("-1")

        return record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if is_conflict_with_empty_repository(response) or is_gone_with_feature_disabled(response):
            # The CDK IGNORE action still calls parse_response; guard against non-array error bodies.
            return
        yield from super().parse_response(
            response=response,
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )


class SemiIncrementalMixin(CheckpointMixin):
    """
    Semi incremental streams are also incremental but with one difference, they:
      - read all records;
      - output only new records.
    This means that semi incremental streams read all records (like full_refresh streams) but do filtering directly
    in the code and output only latest records (like incremental streams).
    """

    cursor_field = "updated_at"

    # This flag is used to indicate that current stream supports `sort` and `direction` request parameters and that
    # we should break processing records if possible. If `sort` is set to `updated` and `direction` is set to `desc`
    # this means that latest records will be at the beginning of the response and after we processed those latest
    # records we can just stop and not process other record. This will increase speed of each incremental stream
    # which supports those 2 request parameters. Of the remaining Python streams only `PullRequests` (a technical
    # parent, see below) still uses it; the declarative equivalent is `is_data_feed: true` in `manifest.yaml`.
    is_sorted = False

    def __init__(self, start_date: str = "", **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self._starting_point_cache = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    @property
    def slice_keys(self):
        if hasattr(self, "repositories"):
            return ["repository"]
        return ["organization"]

    record_slice_key = slice_keys

    def convert_cursor_value(self, value):
        return value

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        if self.is_sorted == "asc":
            return self.page_size

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state
        object and returning an updated state object.
        """
        slice_value = getter(latest_record, self.record_slice_key)
        updated_state = self.convert_cursor_value(latest_record[self.cursor_field])
        stream_state_value = current_stream_state.get(slice_value, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(slice_value, {})[self.cursor_field] = updated_state
        return current_stream_state

    def _get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        if stream_state:
            state_path = [stream_slice[k] for k in self.slice_keys] + [self.cursor_field]
            stream_state_value = getter(stream_state, state_path, strict=False)
            if stream_state_value:
                if self._start_date:
                    return max(self._start_date, stream_state_value)
                return stream_state_value
        return self._start_date

    def get_starting_point(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        cache_key = tuple([stream_slice[k] for k in self.slice_keys])
        if cache_key not in self._starting_point_cache:
            self._starting_point_cache[cache_key] = self._get_starting_point(stream_state, stream_slice)
        return self._starting_point_cache[cache_key]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state, stream_slice=stream_slice)
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            cursor_value = self.convert_cursor_value(record[self.cursor_field])
            if not start_point or cursor_value > start_point:
                yield record
                self.state = self._get_updated_state(self.state, record)
            elif self.is_sorted == "desc" and cursor_value < start_point:
                break

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        self._starting_point_cache.clear()
        yield from super().stream_slices(**kwargs)
