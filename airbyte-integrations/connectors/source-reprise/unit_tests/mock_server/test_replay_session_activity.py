# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""replay_session_activity: cursor transformation, incremental state, slicing, RemoveFields."""

from typing import Any, List, Mapping, Optional
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import (
    NOW,
    config,
    data_request,
    data_response,
    login_request,
    login_response,
)


_STREAM_NAME = "replay_session_activity"


def _record(activity_id: str, session_created_at: Optional[str] = "2026-08-20 01:00:00") -> dict:
    record: dict = {"activity_id": activity_id, "session_id": f"session-{activity_id}"}
    if session_created_at is not None:
        record["session_created_at"] = session_created_at
    return record


def _read(connector_config: Mapping[str, Any], state: Optional[List[Any]] = None) -> Any:
    return read(
        get_source(config=connector_config, state=state),
        config=connector_config,
        catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build(),
        state=state,
    )


@freezegun.freeze_time(NOW)
class TestReplaySessionActivity(TestCase):
    @HttpMocker()
    def test_when_read_then_state_advances_to_max_since_created_at(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            data_request(_STREAM_NAME),
            data_response(
                [
                    _record("a1", "2026-08-20 03:00:00"),
                    _record("a2", "2026-08-20 07:45:12"),  # max
                    _record("a3", "2026-08-20 05:00:00"),  # out of order on purpose
                ]
            ),
        )

        output = _read(config())

        assert output.errors == []
        assert [record.record.data["since_created_at"] for record in output.records] == [
            "2026-08-20 03:00:00",
            "2026-08-20 07:45:12",
            "2026-08-20 05:00:00",
        ]
        assert output.most_recent_state.stream_state.__dict__ == {"since_created_at": "2026-08-20 07:45:12"}

    @HttpMocker()
    def test_given_state_when_read_then_three_day_lookback_is_applied_and_window_is_sliced_per_day(self, http_mocker: HttpMocker) -> None:
        # State is 2026-08-20 10:00:00; lookback_window P3D pulls the start back to
        # 2026-08-17 10:00:00 (still above the configured start_time floor), and step P1D
        # then cuts that window into four requests.
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"since_created_at": "2026-08-20 10:00:00"}).build()
        connector_config = config(start_time="2026-08-17 00:00:00")
        expected_windows = [
            ("2026-08-17 10:00:00", "2026-08-18 09:59:59"),
            ("2026-08-18 10:00:00", "2026-08-19 09:59:59"),
            ("2026-08-19 10:00:00", "2026-08-20 09:59:59"),
            ("2026-08-20 10:00:00", "2026-08-20 12:00:00"),
        ]

        http_mocker.post(login_request(), login_response())
        for index, (start, end) in enumerate(expected_windows):
            http_mocker.get(
                data_request(_STREAM_NAME, start=start, end=end),
                data_response([_record(f"slice-{index}", f"{start[:10]} 11:00:00")]),
            )

        output = _read(connector_config, state=state)

        assert output.errors == []
        # One record per slice; slices are fetched concurrently, so compare as a set.
        assert {record.record.data["activity_id"] for record in output.records} == {f"slice-{i}" for i in range(4)}

    @HttpMocker()
    def test_given_blank_session_created_at_when_read_then_records_are_still_emitted(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            data_request(_STREAM_NAME),
            data_response(
                [
                    _record("with-cursor", "2026-08-20 03:00:00"),
                    _record("empty-string", ""),
                    _record("explicit-null", None),
                    {"activity_id": "absent-key", "session_id": "session-absent-key"},
                ]
            ),
        )

        output = _read(config())

        assert output.errors == []
        assert [record.record.data["activity_id"] for record in output.records] == [
            "with-cursor",
            "empty-string",
            "explicit-null",
            "absent-key",
        ]
        # The AddFields expression yields None for blank/missing values, and a None-valued
        # field is not serialized into the record, so `since_created_at` is simply absent.
        assert output.records[0].record.data["since_created_at"] == "2026-08-20 03:00:00"
        for record in output.records[1:]:
            assert "since_created_at" not in record.record.data
        # Cursor-less records do not drag the state backwards.
        assert output.most_recent_state.stream_state.__dict__ == {"since_created_at": "2026-08-20 03:00:00"}

    @HttpMocker()
    def test_when_read_then_visitor_name_and_distinct_user_are_removed(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            data_request(_STREAM_NAME),
            data_response(
                [
                    {
                        "activity_id": "a1",
                        "session_id": "session-a1",
                        "session_created_at": "2026-08-20 02:00:00",
                        "visitor_key": "visitor-key-1",
                        "visitor_company": "Acme",
                        "visitor_name": "Jane Doe",
                        "distinct_user": "jane.doe@acme.test",
                    }
                ]
            ),
        )

        output = _read(config())

        assert output.errors == []
        emitted = output.records[0].record.data
        assert "visitor_name" not in emitted
        assert "distinct_user" not in emitted
        # Neighbouring visitor fields must survive; RemoveFields must not be over-broad.
        assert emitted["visitor_key"] == "visitor-key-1"
        assert emitted["visitor_company"] == "Acme"
