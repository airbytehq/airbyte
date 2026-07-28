#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder


_EVENT_TYPES = [
    "setup_intent.canceled",
    "setup_intent.created",
    "setup_intent.requires_action",
    "setup_intent.setup_failed",
    "setup_intent.succeeded",
]

_STREAM_NAME = "setup_attempts"
_NOW_IMPORT = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_SETUP_INTENT_ID_1 = "setup_intent_id_1"
_SETUP_INTENT_ID_2 = "setup_intent_id_2"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)

_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}


def get_dates():
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=60)
    return now, start_date


def _config(now) -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(now - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    config["url_base"] = _CONFIG["url_base"]
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class FullRefreshTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    def test_given_one_page_when_read_then_return_records(self) -> None:
        """Zero-Hardcoding contract read for setup attempts."""
        now, start_date = get_dates()
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 2



@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class IncrementalTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(
        self, config: ConfigBuilder, state: Optional[List[AirbyteStateMessage]], expecting_exception: bool = False
    ) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)

    def test_given_no_state_when_read_then_use_setup_attempts_endpoint(self) -> None:
        now, start_date = get_dates()

        self.set_specmatic_expectation(
            path="/v1/setup_intents",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/setup_intents",
                "has_more": False,
                "data": [
                    {"id": _SETUP_INTENT_ID_1, "object": "setup_intent", "created": int(start_date.timestamp())},
                    {"id": _SETUP_INTENT_ID_2, "object": "setup_intent", "created": int(start_date.timestamp())},
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/setup_attempts",
            query={
                "setup_intent": _SETUP_INTENT_ID_1,
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/setup_attempts",
                "has_more": False,
                "data": [
                    {"id": "sa_1", "object": "setup_attempt", "created": int(start_date.timestamp()), "setup_intent": _SETUP_INTENT_ID_1}
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/setup_attempts",
            query={
                "setup_intent": _SETUP_INTENT_ID_2,
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/setup_attempts",
                "has_more": False,
                "data": [
                    {"id": "sa_2", "object": "setup_attempt", "created": int(start_date.timestamp()), "setup_intent": _SETUP_INTENT_ID_2},
                    {"id": "sa_3", "object": "setup_attempt", "created": int(start_date.timestamp()), "setup_intent": _SETUP_INTENT_ID_2},
                ],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date), [])
        assert len(output.records) == 3

    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self) -> None:
        now, _ = get_dates()
        start_date = now - timedelta(days=40)
        state_datetime = now - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 10
        creation_datetime_of_setup_attempt = int(state_datetime.timestamp()) + 5

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": cursor_value,
                        "data": {"object": {"id": _SETUP_INTENT_ID_1, "object": "setup_intent", "created": cursor_value}},
                    }
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/setup_attempts",
            query={
                "setup_intent": _SETUP_INTENT_ID_1,
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/setup_attempts",
                "has_more": False,
                "data": [
                    {
                        "id": "sa_1",
                        "object": "setup_attempt",
                        "created": creation_datetime_of_setup_attempt,
                        "setup_intent": _SETUP_INTENT_ID_1,
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created": int(state_datetime.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        output = self._read(_config(now).with_start_date(start_date), state)

        assert len(output.records) == 1
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert int(most_recent_state.stream_state.state["created"]) == int(creation_datetime_of_setup_attempt)
