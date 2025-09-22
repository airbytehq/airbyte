# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import (
    NoAuth,
)
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import (
    InterpolatedString,
)
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.call_rate import (
    APIBudget,
    HttpRequestMatcher,
    LimiterMixin,
    MovingWindowCallRatePolicy,
    Rate,
    UnlimitedCallRatePolicy,
)
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpClient, HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.types import Config, EmptyString, StreamState
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
            stream_state=self.state or {},
            stream_slice=_slice,
            records_schema=records_schema,
        )

        for stream_data in self._read_pages(record_generator, self.state, _slice):
            # joining channel logic
            if self.should_join_to_channel(self.config, stream_data):
                self.join_channel(self.config, stream_data)

            current_record = self._extract_record(stream_data, _slice)
            if self.cursor and current_record:
                self.cursor.observe(_slice, current_record)

            yield stream_data

        return


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


MESSAGES_AND_THREADS_RATE = Rate(limit=1, interval=timedelta(seconds=60))


class MessagesAndThreadsApiBudget(APIBudget, LimiterMixin):
    """
    Switches to MovingWindowCallRatePolicy 1 request per minute if rate limits were exceeded.
    """

    def update_from_response(self, request: Any, response: Any) -> None:
        current_policy = self.get_matching_policy(request)
        if response.status_code == 429 and isinstance(current_policy, UnlimitedCallRatePolicy):
            matchers = current_policy._matchers
            self._policies = [
                MovingWindowCallRatePolicy(
                    matchers=matchers,
                    rates=[MESSAGES_AND_THREADS_RATE],
                )
            ]


@dataclass
class MessagesAndThreadsHttpRequester(HttpRequester):
    """
    Redefines Custom API Budget to handle rate limits.
    """

    url_match: str = None
    # redefine this here to set up in InterpolatedRequestOptionsProvider in __post_init__
    request_parameters: Dict[str, Any] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._url = InterpolatedString.create(self.url if self.url else EmptyString, parameters=parameters)
        # deprecated
        self._url_base = InterpolatedString.create(self.url_base if self.url_base else EmptyString, parameters=parameters)
        # deprecated
        self._path = InterpolatedString.create(self.path if self.path else EmptyString, parameters=parameters)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config,
                parameters=parameters,
                request_parameters=self.request_parameters,
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self._authenticator = self.authenticator or NoAuth(parameters=parameters)
        self._http_method = HttpMethod[self.http_method] if isinstance(self.http_method, str) else self.http_method
        self.error_handler = self.error_handler
        self._parameters = parameters

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies  # type: ignore
        else:
            backoff_strategies = None

        api_budget = (
            MessagesAndThreadsApiBudget(
                policies=[
                    UnlimitedCallRatePolicy(
                        matchers=[HttpRequestMatcher(url=self.url_match)],
                    )
                ]
            )
            if self.config.get("credentials", {}).get("option_title") == "Default OAuth2.0 authorization"
            else None
        )
        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            api_budget=api_budget,
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )
