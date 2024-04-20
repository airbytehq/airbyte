# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import List
from unittest import TestCase

import freezegun
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import (
    AirbyteStateBlob,
    AirbyteStreamState,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    FailureType,
    Level,
    StreamDescriptor,
    SyncMode,
)
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder
from integration.response_builder import a_response_with_status
from source_stripe import SourceStripe

_STREAM_NAME = "persons"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_CONFIG = {
    "client_secret": _CLIENT_SECRET,
    "account_id": _ACCOUNT_ID,
}
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _create_config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="persons", sync_mode=sync_mode).build()


def _create_accounts_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.accounts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _create_persons_request(parent_account_id: str = _ACCOUNT_ID) -> StripeRequestBuilder:
    return StripeRequestBuilder.persons_endpoint(parent_account_id, _ACCOUNT_ID, _CLIENT_SECRET)


def _create_events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _create_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("accounts", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=StripePaginationStrategy()
    )


def _create_record(resource: str) -> RecordBuilder:
    return create_record_builder(
        find_template(resource, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created")
    )


def _create_persons_event_record(event_type: str) -> RecordBuilder:
    event_record = create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )

    person_record = create_record_builder(
        find_template("persons", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created")
    )

    return event_record.with_field(NestedPath(["data", "object"]), person_record.build()).with_field(NestedPath(["type"]), event_type)


def emits_successful_sync_status_messages(status_messages: List[AirbyteStreamStatus]) -> bool:
    return (len(status_messages) == 3 and status_messages[0] == AirbyteStreamStatus.STARTED
            and status_messages[1] == AirbyteStreamStatus.RUNNING and status_messages[2] == AirbyteStreamStatus.COMPLETE)


@freezegun.freeze_time(_NOW.isoformat())
class PersonsTest(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_parent_pagination(self, http_mocker):
        # First parent stream accounts first page request
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts").with_id("last_page_record_id")).with_pagination().build(),
        )

        # Second parent stream accounts second page request
        http_mocker.get(
            _create_accounts_request().with_limit(100).with_starting_after("last_page_record_id").build(),
            _create_response().with_record(record=_create_record("accounts").with_id("last_page_record_id")).build(),
        )

        # Persons stream first page request
        http_mocker.get(
            _create_persons_request(parent_account_id="last_page_record_id").with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        # The persons stream makes a final call to events endpoint
        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 4

    @HttpMocker()
    def test_substream_pagination(self, http_mocker):
        # First parent stream accounts first page request
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        # Persons stream first page request
        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons").with_id("last_page_record_id")).with_pagination().build(),
        )

        # Persons stream second page request
        http_mocker.get(
            _create_persons_request().with_limit(100).with_starting_after("last_page_record_id").build(),
            _create_response().with_record(record=_create_record("persons")).with_record(
                record=_create_record("persons")).build(),
        )

        # The persons stream makes a final call to events endpoint
        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 4

    @HttpMocker()
    def test_accounts_400_error(self, http_mocker: HttpMocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            a_response_with_status(400),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())
        error_log_messages = [message for message in actual_messages.logs if message.log.level == Level.ERROR]

        # For Stripe, streams that get back a 400 or 403 response code are skipped over silently without throwing an error as part of
        # this connector's availability strategy
        assert len(actual_messages.get_stream_statuses(_STREAM_NAME)) == 0
        assert len(error_log_messages) > 0

    @HttpMocker()
    def test_persons_400_error(self, http_mocker: HttpMocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        # Persons stream first page request
        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            a_response_with_status(400),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())
        error_log_messages = [message for message in actual_messages.logs if message.log.level == Level.ERROR]

        # For Stripe, streams that get back a 400 or 403 response code are skipped over silently without throwing an error as part of
        # this connector's availability strategy. They are however reported in the log messages
        assert len(actual_messages.get_stream_statuses(_STREAM_NAME)) == 0
        assert len(error_log_messages) > 0

    @HttpMocker()
    def test_accounts_401_error(self, http_mocker: HttpMocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            a_response_with_status(401),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(), expecting_exception=True)

        assert actual_messages.errors[-1].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_persons_401_error(self, http_mocker: HttpMocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        # Persons stream first page request
        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            a_response_with_status(401),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(), expecting_exception=True)

        assert actual_messages.errors[-1].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_persons_403_error(self, http_mocker: HttpMocker):
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        # Persons stream first page request
        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            a_response_with_status(403),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog(), expecting_exception=True)
        error_log_messages = [message for message in actual_messages.logs if message.log.level == Level.ERROR]

        # For Stripe, streams that get back a 400 or 403 response code are skipped over silently without throwing an error as part of
        # this connector's availability strategy
        assert len(actual_messages.get_stream_statuses(_STREAM_NAME)) == 0
        assert len(error_log_messages) > 0

    @HttpMocker()
    def test_incremental_with_recent_state(self, http_mocker: HttpMocker):
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES

        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).with_record(record=_create_persons_event_record(event_type="person.created")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(cursor_datetime).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).build(),
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=state,
        )

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=int(state_datetime.timestamp()))
        assert len(actual_messages.records) == 1

    @HttpMocker()
    def test_incremental_with_deleted_event(self, http_mocker: HttpMocker):
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES

        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).with_record(record=_create_persons_event_record(event_type="person.deleted")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(cursor_datetime).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.deleted")).build(),
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=state,
        )

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=int(state_datetime.timestamp()))
        assert len(actual_messages.records) == 1
        assert actual_messages.records[0].record.data.get("is_deleted")

    @HttpMocker()
    def test_incremental_with_newer_start_date(self, http_mocker):
        start_datetime = _NOW - timedelta(days=7)
        state_datetime = _NOW - timedelta(days=15)
        config = _create_config().with_start_date(start_datetime).build()

        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(start_datetime).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).build(),
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = SourceStripe(config=config, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(
            source,
            config=config,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=state,
        )

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=int(state_datetime.timestamp()))
        assert len(actual_messages.records) == 1

    @HttpMocker()
    def test_rate_limited_parent_stream_accounts(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            [
                a_response_with_status(429),
                _create_response().with_record(record=_create_record("accounts")).build(),
            ],
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_rate_limited_substream_persons(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            [
                a_response_with_status(429),
                _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
            ]
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_rate_limited_incremental_events(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES

        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        # Mock when check_availability is run on the persons incremental stream
        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).with_record(
                record=_create_persons_event_record(event_type="person.created")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(cursor_datetime).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            [
                a_response_with_status(429),
                _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).build(),
            ]
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=state,
        )

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name="persons")
        assert most_recent_state.stream_state == AirbyteStateBlob(updated=int(state_datetime.timestamp()))
        assert len(actual_messages.records) == 1

    @HttpMocker()
    def test_rate_limit_max_attempts_exceeded(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            [
                # Used to pass the initial check_availability before starting the sync
                _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
                a_response_with_status(429),  # Returns 429 on all subsequent requests to test the maximum number of retries
            ]
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        # first error is the actual error, second is to break the Python app with code != 0
        assert list(map(lambda message: message.trace.error.failure_type, actual_messages.errors)) == [FailureType.system_error, FailureType.config_error]

    @HttpMocker()
    def test_incremental_rate_limit_max_attempts_exceeded(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES

        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        # Mock when check_availability is run on the persons incremental stream
        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_persons_event_record(event_type="person.created")).with_record(
                record=_create_persons_event_record(event_type="person.created")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(cursor_datetime).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            a_response_with_status(429),  # Returns 429 on all subsequent requests to test the maximum number of retries
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
        actual_messages = read(
            source,
            config=_CONFIG,
            catalog=_create_catalog(sync_mode=SyncMode.incremental),
            state=state,
        )

        assert len(actual_messages.errors) == 2

    @HttpMocker()
    def test_server_error_parent_stream_accounts(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            [
                a_response_with_status(500),
                _create_response().with_record(record=_create_record("accounts")).build(),
            ],
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_server_error_substream_persons(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            [
                a_response_with_status(500),
                _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
            ]
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    @HttpMocker()
    def test_server_error_max_attempts_exceeded(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _create_accounts_request().with_limit(100).build(),
            _create_response().with_record(record=_create_record("accounts")).build(),
        )

        http_mocker.get(
            _create_persons_request().with_limit(100).build(),
            [
                # Used to pass the initial check_availability before starting the sync
                _create_response().with_record(record=_create_record("persons")).with_record(record=_create_record("persons")).build(),
                a_response_with_status(500),  # Returns 429 on all subsequent requests to test the maximum number of retries
            ]
        )

        http_mocker.get(
            _create_events_request().with_created_gte(_NOW - timedelta(days=30)).with_created_lte(_NOW).with_limit(100).with_types(
                ["person.created", "person.updated", "person.deleted"]).build(),
            _create_response().with_record(record=_create_record("events")).with_record(record=_create_record("events")).build(),
        )

        source = SourceStripe(config=_CONFIG, catalog=_create_catalog(), state=_NO_STATE)
        actual_messages = read(source, config=_CONFIG, catalog=_create_catalog())

        # first error is the actual error, second is to break the Python app with code != 0
        assert list(map(lambda message: message.trace.error.failure_type, actual_messages.errors)) == [FailureType.system_error, FailureType.config_error]
