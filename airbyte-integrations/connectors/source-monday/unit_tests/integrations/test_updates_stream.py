# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import List
from unittest import TestCase

from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .monday_requests import UpdatesRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import UpdatesResponseBuilder
from .monday_responses.records import UpdatesRecordBuilder
from .utils import _YAML_FILE_PATH, read_stream


_NOW = "2024-01-15T12:00:00Z"
_STREAM_NAME = "updates"


def _updates_response(created_at: List[str]):
    response = UpdatesResponseBuilder.updates_response()
    for index, value in enumerate(created_at):
        response.with_record(UpdatesRecordBuilder.updates_record().with_id(str(index)).with_cursor(value))
    return response.build()


@freeze_time(_NOW)
class TestUpdatesStream(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().with_api_token_credentials("api-token").build()

    @property
    def _authenticator(self):
        return ApiTokenAuthenticator(api_token=self._config["credentials"]["api_token"])

    def _mock_two_pages(self, http_mocker: HttpMocker, request_builder_factory) -> None:
        http_mocker.post(
            request_builder_factory().build(),
            _updates_response(["2024-01-12T09:00:00Z"] * 99 + ["2024-01-14T10:00:00Z"]),
        )
        http_mocker.post(
            request_builder_factory().with_page(2).build(),
            _updates_response(["2024-01-13T09:00:00Z"]),
        )

    def test_discover_exposes_incremental_with_created_at_cursor(self):
        catalog = YamlDeclarativeSource(path_to_yaml=_YAML_FILE_PATH, config=self._config, catalog=None, state=None).discover(
            logging.getLogger("airbyte"), self._config
        )
        updates = next(stream for stream in catalog.streams if stream.name == _STREAM_NAME)

        assert set(updates.supported_sync_modes) == {SyncMode.full_refresh, SyncMode.incremental}
        assert updates.default_cursor_field == ["created_at"]
        assert updates.source_defined_cursor

    @HttpMocker()
    def test_full_refresh_reads_every_page_without_date_filter(self, http_mocker):
        self._mock_two_pages(http_mocker, lambda: UpdatesRequestBuilder.updates_endpoint(self._authenticator))

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 101

    @HttpMocker()
    def test_incremental_without_state_reads_every_update_and_saves_latest_created_at(self, http_mocker):
        self._mock_two_pages(http_mocker, lambda: UpdatesRequestBuilder.updates_endpoint(self._authenticator))

        output = read_stream(_STREAM_NAME, SyncMode.incremental, self._config)

        assert len(output.records) == 101
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2024-01-14T10:00:00Z"}

    @HttpMocker()
    def test_incremental_with_state_filters_by_created_at_minus_lookback(self, http_mocker):
        self._mock_two_pages(
            http_mocker,
            lambda: UpdatesRequestBuilder.updates_endpoint(self._authenticator).with_date_range("2024-01-11T08:30", "2024-01-15T12:00"),
        )
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": "2024-01-12T08:30:00Z"}).build()

        output = read_stream(_STREAM_NAME, SyncMode.incremental, self._config, state)

        assert len(output.records) == 101
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2024-01-14T10:00:00Z"}
