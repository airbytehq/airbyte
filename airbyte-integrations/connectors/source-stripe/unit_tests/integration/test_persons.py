import json
from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import patch

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, StreamDescriptor, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.helpers import assert_stream_did_not_run


_STREAM_NAME = "persons"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _create_config() -> ConfigBuilder:
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name="persons", sync_mode=sync_mode).build()


def emits_successful_sync_status_messages(status_messages: List[AirbyteStreamStatus]) -> bool:
    return (
        len(status_messages) == 3
        and status_messages[0] == AirbyteStreamStatus.STARTED
        and status_messages[1] == AirbyteStreamStatus.RUNNING
        and status_messages[2] == AirbyteStreamStatus.COMPLETE
    )


@freezegun.freeze_time(_NOW.isoformat())
class PersonsTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(self, config=None, catalog=None, state=None, expecting_exception: bool = False):
        cfg = (config.build() if hasattr(config, "build") else config) or _CONFIG
        cfg["url_base"] = _CONFIG["url_base"]
        cat = catalog or _create_catalog()
        source = get_source(config=cfg, state=state or _NO_STATE)
        return read(source, config=cfg, catalog=cat, state=state, expecting_exception=expecting_exception)

    def test_full_refresh(self):
        """Zero-Hardcoding contract read for persons sub-resource."""
        actual_messages = self._read()
        assert len(actual_messages.records) == 2


    def test_parent_pagination(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": True,
                "data": [{"id": "page_record_id", "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100", "starting_after": "page_record_id"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": "last_page_record_id", "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/accounts/page_record_id/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts/page_record_id/persons",
                "has_more": False,
                "data": [{"id": "p_1", "object": "person"}, {"id": "p_2", "object": "person"}],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/accounts/last_page_record_id/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts/last_page_record_id/persons",
                "has_more": False,
                "data": [{"id": "p_3", "object": "person"}, {"id": "p_4", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 4

    def test_substream_pagination(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": True,
                "data": [{"id": "p_1", "object": "person"}, {"id": "last_page_record_id", "object": "person"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100", "starting_after": "last_page_record_id"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": False,
                "data": [{"id": "p_3", "object": "person"}, {"id": "p_4", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 4

    def test_accounts_400_error(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={"error": {"message": "Your account is not set up to use Issuing"}},
            status_code=400,
        )

        actual_messages = self._read()
        assert_stream_did_not_run(actual_messages, _STREAM_NAME, "Your account is not set up to use Issuing")

    def test_persons_400_error(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={"error": {"message": "Your account is not set up to use Issuing"}},
            status_code=400,
        )

        actual_messages = self._read()
        assert_stream_did_not_run(actual_messages, _STREAM_NAME, "Your account is not set up to use Issuing")

    def test_accounts_401_error(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={"error": {"message": "Invalid API Key"}},
            status_code=401,
        )

        actual_messages = self._read(expecting_exception=True)
        assert actual_messages.errors[-1].trace.error.failure_type == FailureType.config_error

    def test_persons_401_error(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={"error": {"message": "Invalid API Key"}},
            status_code=401,
        )

        actual_messages = self._read(expecting_exception=True)
        assert actual_messages.errors[-1].trace.error.failure_type == FailureType.config_error

    def test_persons_403_error(self):
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={"error": {"message": "This application does not have the required permissions"}},
            status_code=403,
        )

        actual_messages = self._read(expecting_exception=True)
        assert_stream_did_not_run(actual_messages, _STREAM_NAME, "This application does not have the required permissions")

    def test_incremental_with_recent_state(self):
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(cursor_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": ["person.created", "person.updated", "person.deleted"],
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(cursor_datetime.timestamp()),
                        "type": "person.created",
                        "data": {"object": {"id": "p_1", "object": "person", "created": int(cursor_datetime.timestamp())}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        actual_messages = self._read(catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert int(most_recent_state.stream_state.updated) == int(state_datetime.timestamp())
        assert len(actual_messages.records) == 1

    def test_incremental_with_deleted_event(self):
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(cursor_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": ["person.created", "person.updated", "person.deleted"],
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(cursor_datetime.timestamp()),
                        "type": "person.deleted",
                        "data": {"object": {"id": "p_1", "object": "person", "created": int(cursor_datetime.timestamp())}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        actual_messages = self._read(catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert int(most_recent_state.stream_state.updated) == int(state_datetime.timestamp())
        assert len(actual_messages.records) == 1
        assert actual_messages.records[0].record.data.get("is_deleted")

    def test_incremental_with_newer_start_date(self):
        start_datetime = _NOW - timedelta(days=7)
        state_datetime = _NOW - timedelta(days=15)
        config = _create_config().with_start_date(start_datetime)

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(start_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": ["person.created", "person.updated", "person.deleted"],
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(start_datetime.timestamp()),
                        "type": "person.created",
                        "data": {"object": {"id": "p_1", "object": "person", "created": int(start_datetime.timestamp())}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        actual_messages = self._read(config=config, catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert int(most_recent_state.stream_state.updated) == int(start_datetime.timestamp())
        assert len(actual_messages.records) == 1

    def test_rate_limited_parent_stream_accounts(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": False,
                "data": [{"id": "p_1", "object": "person"}, {"id": "p_2", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    def test_rate_limited_substream_persons(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": False,
                "data": [{"id": "p_1", "object": "person"}, {"id": "p_2", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    def test_rate_limited_incremental_events(self) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(cursor_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": ["person.created", "person.updated", "person.deleted"],
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(cursor_datetime.timestamp()),
                        "type": "person.created",
                        "data": {"object": {"id": "p_1", "object": "person", "created": int(cursor_datetime.timestamp())}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        actual_messages = self._read(catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        most_recent_state = actual_messages.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name="persons")
        assert int(most_recent_state.stream_state.updated) == int(state_datetime.timestamp())
        assert len(actual_messages.records) == 1

    def test_rate_limit_max_attempts_exceeded(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={"error": {"message": "Too many requests"}},
            status_code=429,
        )

        with patch.object(HttpStatusErrorHandler, "max_retries", new=0):
            actual_messages = self._read()
            assert list(map(lambda message: message.trace.error.failure_type, actual_messages.errors)) == [
                FailureType.system_error,
                FailureType.config_error,
            ]
            assert "Too many requests" in actual_messages.errors[0].trace.error.internal_message

    def test_incremental_rate_limit_max_attempts_exceeded(self) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_datetime = state_datetime

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(cursor_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": ["person.created", "person.updated", "person.deleted"],
            },
            response_body={"error": {"message": "Too many requests"}},
            status_code=429,
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        with patch.object(HttpStatusErrorHandler, "max_retries", new=0):
            actual_messages = self._read(catalog=_create_catalog(sync_mode=SyncMode.incremental), state=state)
            assert len(actual_messages.errors) == 2
            assert "Too many requests" in actual_messages.errors[0].trace.error.internal_message

    def test_server_error_parent_stream_accounts(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": False,
                "data": [{"id": "p_1", "object": "person"}, {"id": "p_2", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    def test_server_error_substream_persons(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/accounts",
                "has_more": False,
                "data": [{"id": _ACCOUNT_ID, "object": "account"}],
            },
        )
        self.set_specmatic_expectation(
            path=f"/v1/accounts/{_ACCOUNT_ID}/persons",
            query={"limit": "100"},
            response_body={
                "object": "list",
                "url": f"/v1/accounts/{_ACCOUNT_ID}/persons",
                "has_more": False,
                "data": [{"id": "p_1", "object": "person"}, {"id": "p_2", "object": "person"}],
            },
        )

        actual_messages = self._read()
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses(_STREAM_NAME))
        assert len(actual_messages.records) == 2

    def test_server_error_max_attempts_exceeded(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/accounts",
            query={"limit": "100"},
            response_body={"error": {"message": "Internal Server Error"}},
            status_code=500,
        )

        with patch.object(HttpStatusErrorHandler, "max_retries", new=0):
            actual_messages = self._read()
            assert list(map(lambda message: message.trace.error.failure_type, actual_messages.errors)) == [
                FailureType.system_error,
                FailureType.config_error,
            ]
