# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from dataclasses import InitVar, dataclass, field
from datetime import timedelta
from functools import partial
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.types import Config
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


LOGGER = logging.getLogger("airbyte_logger")


class JoinChannelsStream(HttpStream):
    """
    This class is a special stream which joins channels because the Slack API only returns messages from channels this bot is in.
    Its responses should only be logged for debugging reasons, not read as records.
    """

    url_base = "https://slack.com/api/"
    http_method = "POST"
    primary_key = "id"

    def __init__(self, channel_filter: List[str] = None, **kwargs):
        self.channel_filter = channel_filter or []
        super().__init__(**kwargs)

    def path(self, **kwargs) -> str:
        return "conversations.join"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable:
        """
        Override to simply indicate that the specific channel was joined successfully.
        This method should not return any data, but should return an empty iterable.
        """
        is_ok = response.json().get("ok", False)
        if is_ok:
            self.logger.info(f"Successfully joined channel: {stream_slice['channel_name']}")
        else:
            self.logger.info(f"Unable to joined channel: {stream_slice['channel_name']}. Reason: {response.json()}")
        return []

    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        if stream_slice:
            return {"channel": stream_slice.get("channel")}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        The pagination is not applicable to this Service Stream.
        """
        return None


@dataclass
class ChannelMembersExtractor(DpathExtractor):
    """
    Transform response from a list of strings to list dicts:
    from: ['aa', 'bb']
    to: [{'member_id': 'aa'}, {{'member_id': 'bb'}]
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        records = super().extract_records(response)
        return [{"member_id": record} for record in records]


class ChannelsRetriever(SimpleRetriever):
    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
        self.record_selector.transformations = []

    def should_join_to_channel(self, config: Mapping[str, Any], record: Record) -> bool:
        """
        The `is_member` property indicates whether the API Bot is already assigned / joined to the channel.
        https://api.slack.com/types/conversation#booleans
        """
        return config["join_channels"] and not record.get("is_member")

    def make_join_channel_slice(self, channel: Mapping[str, Any]) -> Mapping[str, Any]:
        channel_id: str = channel.get("id")
        channel_name: str = channel.get("name")
        LOGGER.info(f"Joining Slack Channel: `{channel_name}`")
        return {"channel": channel_id, "channel_name": channel_name}

    def join_channels_stream(self, config) -> JoinChannelsStream:
        token = config["credentials"].get("api_token") or config["credentials"].get("access_token")
        authenticator = TokenAuthenticator(token)
        channel_filter = config["channel_filter"]
        return JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)

    def join_channel(self, config: Mapping[str, Any], record: Mapping[str, Any]):
        list(
            self.join_channels_stream(config).read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice=self.make_join_channel_slice(record),
            )
        )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        _slice = stream_slice or StreamSlice(partition={}, cursor_slice={})  # None-check

        record_generator = partial(
            self._parse_records,
            stream_slice=_slice,
            records_schema=records_schema,
        )

        for stream_data in self._read_pages(record_generator, _slice):
            if self.should_join_to_channel(self.config, stream_data):
                self.join_channel(self.config, stream_data)

            yield stream_data


@dataclass
class RateLimitLoggingBackoffStrategy(BackoffStrategy):
    """
    Custom backoff strategy that wraps WaitTimeFromHeader behavior and logs
    Slack rate-limit response headers on every 429 response. This helps
    diagnose whether the connection is on Tier 3 (Marketplace, 50+ req/min)
    or the lower non-Marketplace rate (1 req/min).

    Emits RATE_LIMIT_DEBUG log lines with Retry-After values, the API method
    that was rate-limited, and all X-Rate-Limit-* headers from Slack's response.
    """

    header: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    config: Config

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.header = InterpolatedString.create(self.header, parameters=parameters)

    @staticmethod
    def _get_numeric_value_from_header(response: requests.Response, header_name: str) -> Optional[float]:
        header_value = response.headers.get(header_name)
        if header_value is None:
            return None
        try:
            return float(header_value)
        except ValueError:
            return None

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        header_value = None
        if isinstance(response_or_exception, requests.Response):
            header = self.header.eval(config=self.config)
            header_value = self._get_numeric_value_from_header(response_or_exception, header)

            # Log all rate-limit-related headers for diagnostics
            if response_or_exception.status_code == 429:
                retry_after = response_or_exception.headers.get("Retry-After", "NOT_SET")
                rate_limit_headers = {
                    k: v
                    for k, v in response_or_exception.headers.items()
                    if k.lower().startswith("retry-after") or k.lower().startswith("x-rate-limit")
                }
                url = ""
                if response_or_exception.request:
                    url = str(response_or_exception.request.url or "")
                    if "?" in url:
                        url = url.split("?")[0]
                LOGGER.info(
                    "RATE_LIMIT_DEBUG: 429 received | Retry-After=%s | backoff_time=%s | attempt=%d | url=%s | all_rate_headers=%s",
                    retry_after,
                    header_value,
                    attempt_count,
                    url,
                    rate_limit_headers,
                )
        return header_value


@dataclass
class ThreadsLoggingPartitionRouter(SubstreamPartitionRouter):
    """
    Thin wrapper around SubstreamPartitionRouter that logs reply_count stats
    from parent messages. Emits a summary every 1000 parent records so we can
    confirm the threads stream behavior without affecting normal performance.

    Log format: THREADS_DEBUG: channel=<id> | total_messages=N | with_replies=N | without_replies=N | max_reply_count=N
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        total = 0
        with_replies = 0
        without_replies = 0
        max_reply_count = 0
        current_channel = ""

        for stream_slice in super().stream_slices():
            parent_slice = stream_slice.partition.get("parent_slice", {})
            channel = parent_slice.get("channel", "unknown")

            # When channel changes, flush the summary for the previous channel
            if channel != current_channel and total > 0:
                LOGGER.info(
                    "THREADS_DEBUG: channel=%s | total_messages=%d | with_replies=%d | without_replies=%d | max_reply_count=%d",
                    current_channel,
                    total,
                    with_replies,
                    without_replies,
                    max_reply_count,
                )
                total = 0
                with_replies = 0
                without_replies = 0
                max_reply_count = 0
            current_channel = channel

            # Count reply_count from the extra_fields if present, otherwise
            # we can't tell — but the slice itself was created from a parent record
            reply_count = stream_slice.extra_fields.get("reply_count", 0) if stream_slice.extra_fields else 0
            total += 1
            if reply_count and int(reply_count) >= 1:
                with_replies += 1
                max_reply_count = max(max_reply_count, int(reply_count))
            else:
                without_replies += 1

            # Periodic log every 1000 messages to avoid flooding
            if total % 1000 == 0:
                LOGGER.info(
                    "THREADS_DEBUG: channel=%s | progress=%d messages | with_replies=%d | without_replies=%d | max_reply_count=%d",
                    current_channel,
                    total,
                    with_replies,
                    without_replies,
                    max_reply_count,
                )

            yield stream_slice

        # Final flush for the last channel
        if total > 0:
            LOGGER.info(
                "THREADS_DEBUG: channel=%s | total_messages=%d | with_replies=%d | without_replies=%d | max_reply_count=%d",
                current_channel,
                total,
                with_replies,
                without_replies,
                max_reply_count,
            )


class ThreadsStateMigration(StateMigration):
    """
    The logic for incrementally syncing threads is not very obvious, so buckle up.
    To get all messages in a thread, one must specify the channel and timestamp of the parent (first) message of that thread,
    basically its ID.
    One complication is that threads can be updated at Any time in the future. Therefore, if we wanted to comprehensively sync data
    i.e: get every single response in a thread, we'd have to read every message in the slack instance every time we ran a sync,
    because otherwise there is no way to guarantee that a thread deep in the past didn't receive a new message.
    A pragmatic workaround is to say we want threads to be at least N days fresh i.e: look back N days into the past,
    get every message since, and read all of the thread responses. This is essentially the approach we're taking here via slicing:
    create slices from N days into the past and read all messages in threads since then. We could optionally filter out records we have
    already read, but that's omitted to keep the logic simple to reason about.
    Good luck.
    """

    config: Config

    def __init__(self, config: Config):
        self._config = config

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not stream_state:
            return {}

        start_date_state = ab_datetime_parse(self._config["start_date"]).timestamp()  # start date is required
        # for migrated state
        if stream_state.get("states"):
            for state in stream_state["states"]:
                start_date_state = max(start_date_state, float(state.get("cursor", {}).get("float_ts", start_date_state)))
        # for old-stype state
        if stream_state.get("float_ts"):
            start_date_state = max(start_date_state, float(stream_state["float_ts"]))

        lookback_window = timedelta(days=self._config.get("lookback_window", 0))  # lookback window in days
        final_state = {"float_ts": (ab_datetime_parse(int(start_date_state)) - lookback_window).timestamp()}
        stream_state["parent_state"] = {"channel_messages": final_state}

        return stream_state
