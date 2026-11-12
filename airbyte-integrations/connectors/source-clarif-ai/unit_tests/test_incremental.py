# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2026-01-01T00:00:00Z",
}
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")

# Clarifai returns `modified_at` with nanosecond precision (9 fractional digits).
_OLD = "2026-10-02T17:05:11.904417302Z"
_NEW = "2026-10-14T09:41:55.568082659Z"
_EXPECTED_STATE = "2026-10-14T09:41:55.568082Z"


def _catalog(stream_name):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            [
                {"json": {"apps": [{"id": "app1", "modified_at": _OLD}, {"id": "app2", "modified_at": _NEW}]}},
                {"json": {"apps": []}},
            ],
        )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog("applications"))

    # The cursor value is emitted at microsecond precision, the precision the state is stored in.
    assert [(r.record.data["id"], r.record.data["modified_at"]) for r in output.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", _EXPECTED_STATE),
    ]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": _EXPECTED_STATE}


@pytest.mark.parametrize(
    "modified_at, expected_state",
    [
        ("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568000Z"),
        ("2026-10-14T09:41:55Z", "2026-10-14T09:41:55.000000Z"),
    ],
    ids=["micros", "millis", "no_fraction"],
)
def test_applications_state_advances_for_other_protobuf_timestamp_precisions(modified_at, expected_state):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, [{"json": {"apps": [{"id": "app1", "modified_at": modified_at}]}}, {"json": {"apps": []}}])
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog("applications"))

    # Values with at most 6 fractional digits are emitted unchanged.
    assert [(r.record.data["id"], r.record.data["modified_at"]) for r in output.records] == [("app1", modified_at)]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": expected_state}


def test_applications_second_read_carries_state_forward():
    state = StateBuilder().with_stream_state("applications", {"modified_at": "2026-10-10T00:00:00.000000Z"}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            [
                {"json": {"apps": [{"id": "app1", "modified_at": _OLD}, {"id": "app2", "modified_at": _NEW}]}},
                {"json": {"apps": []}},
            ],
        )
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=_catalog("applications"), state=state)

    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": _EXPECTED_STATE}


@pytest.mark.parametrize("stream_name, records_key", [("datasets", "datasets"), ("models", "models")])
def test_per_app_substream_state_advances_to_newest_nanosecond_modified_at(stream_name, records_key):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            [{"json": {"apps": [{"id": "app1", "modified_at": _OLD}]}}, {"json": {"apps": []}}],
        )
        mocker.get(
            re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{stream_name}(?:\?.*)?$"),
            [
                {"json": {records_key: [{"id": "a", "modified_at": _OLD}, {"id": "b", "modified_at": _NEW}]}},
                {"json": {records_key: []}},
            ],
        )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog(stream_name))

    assert sorted(record.record.data["id"] for record in output.records) == ["a", "b"]
    states = output.most_recent_state.stream_state.__dict__["states"]
    assert [(s["partition"]["app_id"], s["cursor"]) for s in states] == [("app1", {"modified_at": _EXPECTED_STATE})]
