# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""replicate_session_activity: viewer PII redaction and viewer_is_internal classification."""

from typing import Any, Mapping
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import (
    NOW,
    config,
    data_request,
    data_response,
    login_request,
    login_response,
)


_STREAM_NAME = "replicate_session_activity"

_API_RECORDS = [
    {"session_id": "s1", "session_date": "2026-08-20 02:00:00", "viewer": "USER@example.com"},
    {"session_id": "s2", "session_date": "2026-08-20 03:00:00", "viewer": "user@elsewhere.com"},
    {"session_id": "s3", "session_date": "2026-08-20 04:00:00", "viewer": "  Bob@Other.IO "},
    {"session_id": "s4", "session_date": "2026-08-20 05:00:00", "viewer": None},
]


def _read(connector_config: Mapping[str, Any]) -> Any:
    return read(
        get_source(config=connector_config),
        config=connector_config,
        catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build(),
    )


def _by_session_id(output: Any) -> Mapping[str, Mapping[str, Any]]:
    return {record.record.data["session_id"]: record.record.data for record in output.records}


@freezegun.freeze_time(NOW)
class TestViewerPii(TestCase):
    @HttpMocker()
    def test_given_include_viewer_pii_absent_when_read_then_viewer_is_redacted(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME), data_response(_API_RECORDS))

        output = _read(config())

        assert output.errors == []
        records = _by_session_id(output)
        assert len(records) == 4
        for session_id, record in records.items():
            assert record.get("viewer") is None, f"{session_id} leaked the raw viewer value"
        # Redaction must not drop the rest of the record.
        assert records["s1"]["since_created_at"] == "2026-08-20 02:00:00"

    @HttpMocker()
    def test_given_include_viewer_pii_false_when_read_then_viewer_is_redacted(self, http_mocker: HttpMocker) -> None:
        connector_config = config(include_viewer_pii=False, internal_email_domains="example.com")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME), data_response(_API_RECORDS))

        output = _read(connector_config)

        assert output.errors == []
        records = _by_session_id(output)
        assert all(record.get("viewer") is None for record in records.values())
        # Classification still happens on the raw value before it is redacted.
        assert records["s1"]["viewer_is_internal"] is True

    @HttpMocker()
    def test_given_include_viewer_pii_true_when_read_then_raw_viewer_is_preserved(self, http_mocker: HttpMocker) -> None:
        connector_config = config(include_viewer_pii=True, internal_email_domains="example.com")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME), data_response(_API_RECORDS))

        output = _read(connector_config)

        assert output.errors == []
        records = _by_session_id(output)
        assert records["s1"]["viewer"] == "USER@example.com"
        assert records["s2"]["viewer"] == "user@elsewhere.com"
        assert records["s3"]["viewer"] == "  Bob@Other.IO "
        assert records["s4"].get("viewer") is None  # null in the API payload

    @HttpMocker()
    def test_given_messy_internal_email_domains_when_read_then_matching_is_trimmed_and_case_insensitive(
        self, http_mocker: HttpMocker
    ) -> None:
        connector_config = config(internal_email_domains="Example.COM, other.io ")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME), data_response(_API_RECORDS))

        output = _read(connector_config)

        assert output.errors == []
        records = _by_session_id(output)
        assert records["s1"]["viewer_is_internal"] is True  # USER@example.com vs "Example.COM"
        assert records["s2"]["viewer_is_internal"] is False  # user@elsewhere.com
        assert records["s3"]["viewer_is_internal"] is True  # "  Bob@Other.IO " vs " other.io "
        assert records["s4"]["viewer_is_internal"] is False  # viewer is null

    @HttpMocker()
    def test_given_no_internal_email_domains_when_read_then_viewer_is_internal_is_false(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME), data_response(_API_RECORDS))

        output = _read(config())

        assert output.errors == []
        records = _by_session_id(output)
        assert [records[key]["viewer_is_internal"] for key in ("s1", "s2", "s3", "s4")] == [False, False, False, False]
