# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `application_feedback` stream on `source-ashby`.

Verifies pagination request bodies against `applicationFeedback.list` and that
free-form `submittedValues` pass through verbatim.
"""

import base64
import json
import logging
from pathlib import Path

import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
_URL = "https://api.ashbyhq.com/applicationFeedback.list"
_CREATED_AFTER_MS = 1704067200000  # 2024-01-01T00:00:00Z in epoch milliseconds


def _get_source():
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )


def _read_application_feedback():
    catalog = CatalogBuilder().with_stream("application_feedback", SyncMode.full_refresh).build()
    return read(_get_source(), _CONFIG, catalog)


def _feedback_record(record_id, **overrides):
    record = {
        "id": record_id,
        "applicationId": "app-1",
        "applicationHistoryId": "hist-1",
        "feedbackFormDefinitionId": "form-def-1",
        "interviewId": "interview-1",
        "interviewEventId": "event-1",
        "submittedAt": "2024-06-01T12:00:00Z",
        "submittedByUser": {
            "id": "user-1",
            "firstName": "Ana",
            "lastName": "Example",
            "email": "ana@example.com",
            "globalRole": "Organization Admin",
            "isEnabled": True,
            "updatedAt": "2024-05-01T00:00:00Z",
        },
        "creditedToUser": {
            "id": "user-2",
            "firstName": "Bob",
            "lastName": "Example",
            "email": "bob@example.com",
            "globalRole": "Interviewer",
            "isEnabled": True,
            "updatedAt": "2024-05-01T00:00:00Z",
        },
        "formDefinition": {
            "sections": [
                {
                    "title": "Scorecard",
                    "fields": [
                        {
                            "isRequired": True,
                            "field": {
                                "id": "field-1",
                                "type": "ValueSingleSelect",
                                "path": "overall_recommendation",
                                "title": "Overall recommendation",
                                "humanReadablePath": "Scorecard / Overall recommendation",
                                "isNullable": False,
                                "selectableValues": [
                                    {"label": "Hire", "value": "hire"},
                                    {"label": "No Hire", "value": "no_hire"},
                                ],
                            },
                        }
                    ],
                }
            ]
        },
        "submittedValues": {"overall_recommendation": "hire", "technical_skills": 4},
    }
    record.update(overrides)
    return record


_PAGE_1 = {
    "success": True,
    "results": [_feedback_record("fb-1"), _feedback_record("fb-2")],
    "moreDataAvailable": True,
    "nextCursor": "cursor-2",
    "syncToken": "tok",
}
_RECORD_3 = _feedback_record("fb-3")
del _RECORD_3["creditedToUser"]
_PAGE_2 = {
    "success": True,
    "results": [_RECORD_3],
    "moreDataAvailable": False,
    "syncToken": "tok",
}


def test_application_feedback_reads_all_pages_with_exact_request_bodies():
    with requests_mock.Mocker() as mocker:
        mocker.post(_URL, [{"json": _PAGE_1}, {"json": _PAGE_2}])
        output = _read_application_feedback()

        assert [message.record.data["id"] for message in output.records] == ["fb-1", "fb-2", "fb-3"]

        assert len(mocker.request_history) == 2
        first_body = mocker.request_history[0].json()
        second_body = mocker.request_history[1].json()
        assert first_body == {"createdAfter": _CREATED_AFTER_MS, "limit": 100}
        assert second_body == {"createdAfter": _CREATED_AFTER_MS, "limit": 100, "cursor": "cursor-2"}

        expected_auth = "Basic " + base64.b64encode(b"test-key:test-key").decode()
        assert mocker.request_history[0].headers["Authorization"] == expected_auth


def test_application_feedback_record_keeps_submitted_values_verbatim():
    with requests_mock.Mocker() as mocker:
        mocker.post(_URL, json=_PAGE_2)
        output = _read_application_feedback()

    record = output.records[0].record.data
    assert record["submittedValues"] == {"overall_recommendation": "hire", "technical_skills": 4}
    assert record["formDefinition"]["sections"][0]["fields"][0]["field"]["selectableValues"][0] == {
        "label": "Hire",
        "value": "hire",
    }


def test_discover_declares_application_feedback_stream():
    catalog = _get_source().discover(logging.getLogger("airbyte"), _CONFIG)
    streams_by_name = {stream.name: stream for stream in catalog.streams}
    stream = streams_by_name["application_feedback"]

    assert stream.source_defined_primary_key == [["id"]]
    assert stream.supported_sync_modes == [SyncMode.full_refresh]
    submitted_values = stream.json_schema["properties"]["submittedValues"]
    assert submitted_values["additionalProperties"] is True
    assert "properties" not in submitted_values
