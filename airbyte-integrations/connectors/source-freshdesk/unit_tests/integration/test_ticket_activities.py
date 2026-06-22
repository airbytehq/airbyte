# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest
from requests_mock import Mocker

from airbyte_cdk import AirbyteTracedException, ConfiguredAirbyteCatalog, FailureType, YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))

from components import TicketActivitiesRetriever  # noqa: E402
from config_builder import ConfigBuilder  # noqa: E402


_DOMAIN = "a-domain.freshdesk.com"
_EXPORT_URL = f"https://{_DOMAIN}/api/v2/export/ticket_activities"
_DOWNLOAD_URL = "https://exports.freshdesk.example/2022-01-01-ticket-activities.json"


def _retriever() -> TicketActivitiesRetriever:
    return TicketActivitiesRetriever(config=ConfigBuilder().domain(_DOMAIN).build(), parameters={})


def _slice(start_time: str = "2022-01-01T00:00:00Z", end_time: str = "2022-01-01T23:59:59Z") -> StreamSlice:
    return StreamSlice(partition={}, cursor_slice={"start_time": start_time, "end_time": end_time})


def _activity(performed_at: str = "01-01-2022 09:33:38 +0000", ticket_id: int = 600) -> dict:
    return {
        "performed_at": performed_at,
        "ticket_id": ticket_id,
        "performer_type": "user",
        "performer_id": 149018,
        "activity": {"status": "Open", "priority": 4},
    }


def _register_export(requests_mock: Mocker, activities: list[dict]) -> None:
    requests_mock.get(_EXPORT_URL, json={"export": {"url": _DOWNLOAD_URL}})
    requests_mock.get(
        _DOWNLOAD_URL,
        json={
            "metadata": {
                "start_at": "01-01-2022 00:00:00 +0000",
                "end_at": "01-01-2022 23:59:59 +0000",
                "activities_count": len(activities),
            },
            "activities_data": activities,
        },
    )


def test_ticket_activities_extracts_downloaded_records(requests_mock: Mocker) -> None:
    _register_export(
        requests_mock,
        [
            _activity(ticket_id=600),
            _activity(performed_at="01-01-2022 09:38:24 +0000", ticket_id=704),
        ],
    )

    records = list(_retriever().read_records({}, _slice()))

    assert [record["ticket_id"] for record in records] == [600, 704]
    assert records[0]["performed_at"] == "2022-01-01T09:33:38Z"
    assert records[0]["export_date"] == "2022-01-01"
    assert records[0]["_airbyte_ticket_activity_id"]
    assert requests_mock.request_history[0].qs["created_at"] == ["2022-01-01"]


def test_ticket_activities_empty_export_returns_no_records(requests_mock: Mocker) -> None:
    _register_export(requests_mock, [])

    assert list(_retriever().read_records({}, _slice())) == []


@pytest.mark.parametrize(
    "export_response_status, export_response_json, download_response_status",
    [
        (404, {}, 200),
        (200, {"export": {}}, 200),
        (200, {"export": {"url": _DOWNLOAD_URL}}, 404),
    ],
)
def test_ticket_activities_not_ready_exports_return_no_records(
    requests_mock: Mocker,
    export_response_status: int,
    export_response_json: dict,
    download_response_status: int,
) -> None:
    requests_mock.get(_EXPORT_URL, status_code=export_response_status, json=export_response_json)
    requests_mock.get(_DOWNLOAD_URL, status_code=download_response_status, json={})

    assert list(_retriever().read_records({}, _slice())) == []


def test_ticket_activities_filters_downloaded_records_to_stream_slice(requests_mock: Mocker) -> None:
    _register_export(
        requests_mock,
        [
            _activity(performed_at="01-01-2022 09:59:59 +0000", ticket_id=1),
            _activity(performed_at="01-01-2022 10:00:00 +0000", ticket_id=2),
            _activity(performed_at="02-01-2022 00:00:00 +0000", ticket_id=3),
        ],
    )

    records = list(
        _retriever().read_records(
            {},
            _slice(start_time="2022-01-01T10:00:00Z", end_time="2022-01-01T23:59:59Z"),
        )
    )

    assert [record["ticket_id"] for record in records] == [2]


def test_ticket_activities_duplicate_ids_are_unique_and_stable(requests_mock: Mocker) -> None:
    duplicated_activity = _activity(ticket_id=600)
    _register_export(requests_mock, [duplicated_activity, duplicated_activity])

    first_read_records = list(_retriever().read_records({}, _slice()))
    second_read_records = list(_retriever().read_records({}, _slice()))

    first_ids = [record["_airbyte_ticket_activity_id"] for record in first_read_records]
    second_ids = [record["_airbyte_ticket_activity_id"] for record in second_read_records]
    assert len(set(first_ids)) == 2
    assert first_ids == second_ids


@pytest.mark.parametrize(
    ("status_code", "failure_type"),
    [(403, FailureType.config_error), (500, FailureType.transient_error)],
)
def test_ticket_activities_export_errors_are_traced(requests_mock: Mocker, status_code: int, failure_type: FailureType) -> None:
    requests_mock.get(_EXPORT_URL, status_code=status_code, json={})

    with pytest.raises(AirbyteTracedException) as exc_info:
        list(_retriever().read_records({}, _slice()))

    assert exc_info.value.failure_type == failure_type


def test_ticket_activities_stream_is_incremental() -> None:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=ConfiguredAirbyteCatalog(streams=[]),
        config=ConfigBuilder().domain(_DOMAIN).build(),
        state=None,
    )

    ticket_activities_stream = next(stream for stream in source.streams({}) if stream.name == "ticket_activities")
    airbyte_stream = ticket_activities_stream.as_airbyte_stream()

    assert airbyte_stream.source_defined_primary_key == [["_airbyte_ticket_activity_id"]]
    assert airbyte_stream.default_cursor_field == ["performed_at"]
