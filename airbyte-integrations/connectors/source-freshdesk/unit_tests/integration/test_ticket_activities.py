# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from requests_mock import Mocker

from airbyte_cdk import AirbyteTracedException, ConfiguredAirbyteCatalog, FailureType, SyncMode, YamlDeclarativeSource
from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read


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


class _FastBackoffStrategy(BackoffStrategy):
    def backoff_time(self, response_or_exception, attempt_count: int) -> float:
        return 0.01


_DOMAIN = "a-domain.freshdesk.com"
_EXPORT_URL = f"https://{_DOMAIN}/api/v2/export/ticket_activities"
_DOWNLOAD_URL = "https://exports.freshdesk.example/2022-01-01-ticket-activities.json"
_SIGNED_URL = "https://activities-export-production.s3.amazonaws.com/x.json?X-Amz-Signature=SECRETSIG"


def _retriever() -> TicketActivitiesRetriever:
    return TicketActivitiesRetriever(
        config=ConfigBuilder().domain(_DOMAIN).build(),
        parameters={},
        backoff_strategy=_FastBackoffStrategy(),
    )


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


def _register_export(
    requests_mock: Mocker,
    activities: list[dict],
    start_at: str = "01-01-2022 00:00:00 +0000",
    end_at: str = "01-01-2022 23:59:59 +0000",
    download_url: str = _DOWNLOAD_URL,
) -> None:
    requests_mock.get(_EXPORT_URL, json={"export": {"url": download_url}})
    requests_mock.get(
        download_url,
        json={
            "metadata": {
                "start_at": start_at,
                "end_at": end_at,
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


def test_ticket_activities_list_export_extracts_downloaded_records(requests_mock: Mocker) -> None:
    requests_mock.get(_EXPORT_URL, json={"export": [{"created_at": "1-1-2022", "url": _DOWNLOAD_URL}]})
    requests_mock.get(_DOWNLOAD_URL, json={"activities_data": [_activity(ticket_id=600), _activity(ticket_id=704)]})

    records = list(_retriever().read_records({}, _slice()))

    assert [record["ticket_id"] for record in records] == [600, 704]
    assert requests_mock.call_count == 2


def test_ticket_activities_list_export_without_url_returns_no_records(requests_mock: Mocker) -> None:
    requests_mock.get(_EXPORT_URL, json={"export": []})
    requests_mock.get(_DOWNLOAD_URL, json={"activities_data": [_activity(ticket_id=600)]})

    assert list(_retriever().read_records({}, _slice())) == []
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    "export_response_json",
    [
        {"export": [{}]},
        {"export": ["not-a-dict", 42]},
        {"export": [{"created_at": "1-1-2022"}]},
        {"export": [{"created_at": "1-1-2022", "download_url": _SIGNED_URL}]},
        {"export": [{"created_at": "1-1-2022", "url": {"href": _SIGNED_URL}}]},
        {"export": {"created_at": "1-1-2022", "link": _SIGNED_URL}},
    ],
)
def test_ticket_activities_unrecognized_export_shape_raises_without_leaking_url(
    requests_mock: Mocker, caplog: pytest.LogCaptureFixture, export_response_json: dict
) -> None:
    requests_mock.get(_EXPORT_URL, json=export_response_json)

    with caplog.at_level(logging.DEBUG, logger="airbyte"), pytest.raises(AirbyteTracedException) as exc_info:
        list(_retriever().read_records({}, _slice()))

    assert exc_info.value.failure_type == FailureType.system_error
    assert "SECRETSIG" not in exc_info.value.message
    assert "SECRETSIG" not in exc_info.value.internal_message
    assert all("SECRETSIG" not in record.getMessage() for record in caplog.records)


@pytest.mark.parametrize("export_response_json", [{"export": {}}, {"export": []}])
def test_ticket_activities_missing_export_logs_info_not_warning(
    requests_mock: Mocker, caplog: pytest.LogCaptureFixture, export_response_json: dict
) -> None:
    requests_mock.get(_EXPORT_URL, json=export_response_json)

    with caplog.at_level(logging.INFO, logger="airbyte"):
        assert list(_retriever().read_records({}, _slice())) == []

    assert not [record for record in caplog.records if record.levelno == logging.WARNING]
    assert any("No ticket activities export was available" in record.getMessage() for record in caplog.records)


def test_ticket_activities_emits_whole_export_for_offset_file_window(requests_mock: Mocker) -> None:
    _register_export(
        requests_mock,
        [
            _activity(performed_at="01-01-2022 09:59:59 +0000", ticket_id=1),
            _activity(performed_at="01-01-2022 10:00:00 +0000", ticket_id=2),
            _activity(performed_at="02-01-2022 00:00:00 +0000", ticket_id=3),
            _activity(performed_at="02-01-2022 09:59:59 +0000", ticket_id=4),
        ],
        start_at="01-01-2022 10:00:00 +0000",
        end_at="02-01-2022 09:59:59 +0000",
    )

    records = list(_retriever().read_records({}, _slice("2022-01-01T13:45:12Z", "2022-01-02T13:45:11Z")))

    assert [record["ticket_id"] for record in records] == [1, 2, 3, 4]
    assert all(record["export_date"] == "2022-01-01" for record in records)
    assert requests_mock.request_history[0].qs["created_at"] == ["2022-01-01"]


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


def test_ticket_activities_retries_rate_limits_then_reads(requests_mock: Mocker) -> None:
    requests_mock.get(
        _EXPORT_URL,
        [
            {"status_code": 429, "json": {}, "headers": {"Retry-After": "0.01"}},
            {"status_code": 200, "json": {"export": {"url": _DOWNLOAD_URL}}},
        ],
    )
    requests_mock.get(
        _DOWNLOAD_URL,
        json={"activities_data": [_activity(ticket_id=600)]},
    )

    records = list(_retriever().read_records({}, _slice()))

    assert [record["ticket_id"] for record in records] == [600]
    assert requests_mock.call_count == 3


def test_ticket_activities_honors_injected_api_budget() -> None:
    budget = APIBudget(policies=[])

    retriever = TicketActivitiesRetriever(
        config=ConfigBuilder().domain(_DOMAIN).build(),
        parameters={},
        api_budget=budget,
    )

    assert retriever._http_client._api_budget is budget


def test_ticket_activities_lookback_is_clamped_to_export_retention() -> None:
    config = ConfigBuilder().domain(_DOMAIN).start_date(datetime(2017, 1, 1)).build()
    before = datetime.now(timezone.utc)
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=ConfiguredAirbyteCatalog(streams=[]),
        config=config,
        state=None,
    )

    stream = next(s for s in source.streams(config) if s.name == "ticket_activities")
    slices = [partition.to_slice() for partition in stream.generate_partitions()]
    after = datetime.now(timezone.utc)

    # Freshdesk keeps each daily export file for 30 days; older slices are guaranteed 404s,
    # so the stream clamps any config start_date to the retention window.
    assert 0 < len(slices) <= 32
    assert slices[0]["start_time"] in {(now - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z") for now in (before, after)}


def _ticket_activities_stream(config: dict, state: list | None = None):
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=ConfiguredAirbyteCatalog(streams=[]),
        config=config,
        state=state,
    )
    return next(stream for stream in source.streams(config) if stream.name == "ticket_activities")


def _cursor_slices(stream) -> list[StreamSlice]:
    return [partition.to_slice() for partition in stream.generate_partitions()]


def _consecutive_dates(start: datetime, end: datetime) -> list[str]:
    return [(start.date() + timedelta(days=i)).isoformat() for i in range((end.date() - start.date()).days + 1)]


def test_ticket_activities_initial_slices_are_midnight_aligned() -> None:
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=5)).replace(hour=13, minute=45, second=12, microsecond=0)
    config = ConfigBuilder().domain(_DOMAIN).start_date(start_date).build()

    slices = _cursor_slices(_ticket_activities_stream(config))
    after = datetime.now(timezone.utc)

    assert [slice_["start_time"][:10] for slice_ in slices] in (_consecutive_dates(start_date, now), _consecutive_dates(start_date, after))
    assert all(slice_["start_time"].endswith("T00:00:00Z") for slice_ in slices)
    assert all(slice_["end_time"].endswith("T23:59:59Z") for slice_ in slices[:-1])


def test_ticket_activities_incremental_slices_from_mid_day_state_cover_every_day() -> None:
    now = datetime.now(timezone.utc)
    state_datetime = (now - timedelta(days=4)).replace(hour=13, minute=45, second=12, microsecond=0)
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="ticket_activities"),
                stream_state=AirbyteStateBlob(performed_at=state_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")),
            ),
        )
    ]
    config = ConfigBuilder().domain(_DOMAIN).build()

    slices = _cursor_slices(_ticket_activities_stream(config, state))
    after = datetime.now(timezone.utc)

    slice_dates = [slice_["start_time"][:10] for slice_ in slices]
    assert slice_dates in [
        [(state_datetime + timedelta(days=i)).date().isoformat() for i in range((end - state_datetime).days + 1)] for end in (now, after)
    ]
    retriever = _retriever()
    assert [retriever._get_export_date(StreamSlice(partition={}, cursor_slice=slice_)) for slice_ in slices] == slice_dates


def test_ticket_activities_consecutive_slices_do_not_lose_or_duplicate_records(requests_mock: Mocker) -> None:
    url_1 = "https://exports.freshdesk.example/2022-01-01-ticket-activities.json"
    url_2 = "https://exports.freshdesk.example/2022-01-02-ticket-activities.json"
    exports = {
        "2022-01-01": {"export": [{"created_at": "1-1-2022", "url": url_1}]},
        "2022-01-02": {"export": [{"created_at": "2-1-2022", "url": url_2}]},
    }
    requests_mock.get(_EXPORT_URL, json=lambda request, context: exports[request.qs["created_at"][0]])
    requests_mock.get(
        url_1,
        json={
            "metadata": {
                "start_at": "01-01-2022 10:00:00 +0000",
                "end_at": "02-01-2022 09:59:59 +0000",
                "activities_count": 3,
            },
            "activities_data": [
                _activity(performed_at="01-01-2022 10:00:00 +0000", ticket_id=1),
                _activity(performed_at="01-01-2022 23:59:59 +0000", ticket_id=2),
                _activity(performed_at="02-01-2022 09:59:59 +0000", ticket_id=3),
            ],
        },
    )
    requests_mock.get(
        url_2,
        json={
            "metadata": {
                "start_at": "02-01-2022 10:00:00 +0000",
                "end_at": "03-01-2022 09:59:59 +0000",
                "activities_count": 2,
            },
            "activities_data": [
                _activity(performed_at="02-01-2022 10:00:00 +0000", ticket_id=4),
                _activity(performed_at="03-01-2022 09:59:59 +0000", ticket_id=5),
            ],
        },
    )

    first = list(_retriever().read_records({}, _slice("2022-01-01T13:45:12Z", "2022-01-02T13:45:11Z")))
    second = list(_retriever().read_records({}, _slice("2022-01-02T13:45:12Z", "2022-01-03T13:45:11Z")))

    assert [record["ticket_id"] for record in first] == [1, 2, 3]
    assert all(record["export_date"] == "2022-01-01" for record in first)
    assert [record["ticket_id"] for record in second] == [4, 5]
    assert all(record["export_date"] == "2022-01-02" for record in second)
    records = first + second
    assert len(records) == 5
    assert len({record["_airbyte_ticket_activity_id"] for record in records}) == 5


def test_ticket_activities_next_sync_does_not_reemit_synced_records(requests_mock: Mocker) -> None:
    day = (datetime.now(timezone.utc) - timedelta(days=2)).date()
    next_day = day + timedelta(days=1)
    next_day_url = "https://exports.freshdesk.example/next-day-ticket-activities.json"
    # UTC+2 account: the next_day file starts at day 22:00Z, before the next_day slice starts.
    download_urls = {day.isoformat(): _DOWNLOAD_URL, next_day.isoformat(): next_day_url}

    def export(request, context):
        url = download_urls.get(request.qs["created_at"][0])
        if url is None:
            context.status_code = 404
            return {}
        return {"export": [{"url": url}]}

    requests_mock.get(_EXPORT_URL, json=export)
    activities = [_activity(performed_at=f"{day:%d-%m-%Y} {hour:02d}:00:00 +0000", ticket_id=hour) for hour in (1, 12, 20)]
    requests_mock.get(_DOWNLOAD_URL, json={"activities_data": activities})
    requests_mock.get(next_day_url, json={"activities_data": [_activity(performed_at=f"{day:%d-%m-%Y} 22:00:00 +0000", ticket_id=22)]})
    config = ConfigBuilder().domain(_DOMAIN).start_date(datetime(day.year, day.month, day.day)).build()
    catalog = CatalogBuilder().with_stream("ticket_activities", SyncMode.incremental).build()

    def sync(state):
        source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
        return entrypoint_read(source, config, catalog, state)

    first_sync = sync(None)
    first_sync_state = first_sync.state_messages[-1].state
    assert sorted(record.record.data["ticket_id"] for record in first_sync.records) == [1, 12, 20, 22]
    assert first_sync_state.stream.stream_state.performed_at == f"{day.isoformat()}T22:00:00Z"

    second_sync_start = len(requests_mock.request_history)
    second_sync = sync([first_sync_state])
    export_dates = [
        request.qs["created_at"][0] for request in requests_mock.request_history[second_sync_start:] if "created_at" in request.qs
    ]
    assert [record.record.data["ticket_id"] for record in second_sync.records] == [22]
    assert min(export_dates) == day.isoformat()


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
