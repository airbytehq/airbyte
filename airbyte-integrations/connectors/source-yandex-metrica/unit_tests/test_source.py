#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest
from source_yandex_metrica.source import SourceYandexMetrica
from source_yandex_metrica.streams import Sessions, Views

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)


logger = logging.getLogger("test_source")
EVALUATE_URL = "https://api-metrica.yandex.net/management/v1/counter/00000000/logrequests/evaluate"
SCHEMA_DIR = Path(__file__).parents[1] / "source_yandex_metrica" / "schemas"


def _load_raw_schema_fields(schema_filename):
    with (SCHEMA_DIR / schema_filename).open() as schema_file:
        return list(json.load(schema_file)["properties"])


def test_streams(config):
    source = SourceYandexMetrica()
    streams = source.streams(config)
    assert len(streams) == 2


@pytest.mark.parametrize(
    "stream_class,schema_filename,prefix,stripped_field",
    [
        pytest.param(Sessions, "sessions.json", "ym:s:", "visitID", id="sessions"),
        pytest.param(Views, "views.json", "ym:pv:", "watchID", id="views"),
    ],
)
def test_get_request_fields_keep_prefix_after_get_json_schema(config, stream_class, schema_filename, prefix, stripped_field):
    stream = next(stream for stream in SourceYandexMetrica().streams(config.copy()) if isinstance(stream, stream_class))

    schema = stream.get_json_schema()

    fields = stream.get_request_fields()
    assert fields == _load_raw_schema_fields(schema_filename)
    assert all(field.startswith(prefix) for field in fields)
    assert stripped_field in schema["properties"]
    assert all("ym:" not in field for field in schema["properties"])


def test_check_connection_success(config, requests_mock):
    requests_mock.get(
        EVALUATE_URL,
        [
            {"json": {"log_request_evaluation": {"possible": True}}},
            {"json": {"log_request_evaluation": {"possible": True}}},
        ],
    )

    assert SourceYandexMetrica().check_connection(logger, config=config) == (True, None)
    assert len(requests_mock.request_history) == 2
    for request, source, schema_filename in zip(requests_mock.request_history, ("visits", "hits"), ("sessions.json", "views.json")):
        assert request.headers["Authorization"] == "Bearer test_token"
        assert request.headers["Content-Type"] == "application/x-ymetrika+json"
        assert parse_qs(urlparse(request.url).query) == {
            "date1": ["2022-07-01"],
            "date2": ["2022-07-02"],
            "source": [source],
            "fields": _load_raw_schema_fields(schema_filename),
        }


@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_check_connection_invalid_api_key(status_code, config, requests_mock):
    config["auth_token"] = "invalid_token"
    requests_mock.get(EVALUATE_URL, status_code=status_code)
    assert SourceYandexMetrica().check_connection(logger, config=config) == (False, "Please check provided credentials")


def test_check_connection_retries_server_error(config, requests_mock, mocker):
    mocker.patch("source_yandex_metrica.streams.time.sleep")
    requests_mock.get(
        EVALUATE_URL,
        [
            {"status_code": 500},
            {"json": {"log_request_evaluation": {"possible": True}}},
            {"status_code": 500},
            {"json": {"log_request_evaluation": {"possible": True}}},
        ],
    )

    assert SourceYandexMetrica().check_connection(logger, config=config) == (True, None)
    assert len(requests_mock.request_history) == 4


def test_read_records_sends_auth_and_exact_create_params(config, mock_all_requests, requests_mock):
    stream = SourceYandexMetrica().streams(config)[0]
    list(stream.read_records(sync_mode=SyncMode.full_refresh))

    requests = requests_mock.request_history
    assert [(request.method, urlparse(request.url).path) for request in requests] == [
        ("POST", "/management/v1/counter/00000000/logrequests"),
        ("GET", "/management/v1/counter/00000000/logrequest/1"),
        ("GET", "/management/v1/counter/00000000/logrequest/1/part/0/download"),
        ("POST", "/management/v1/counter/00000000/logrequest/1/clean"),
    ]
    assert all(request.headers["Authorization"] == "Bearer test_token" for request in requests)
    assert parse_qs(urlparse(requests[0].url).query) == {
        "date1": ["2022-07-01"],
        "date2": ["2022-07-02"],
        "source": ["visits"],
        "fields": _load_raw_schema_fields("sessions.json"),
    }


def test_read_sends_prefixed_fields(config, mock_all_requests, requests_mock):
    stream = next(stream for stream in SourceYandexMetrica().streams(config.copy()) if isinstance(stream, Sessions))
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream.as_airbyte_stream(),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    list(
        SourceYandexMetrica().read(
            logger,
            config,
            catalog,
            state=[
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="sessions"),
                        stream_state=AirbyteStateBlob({"dateTime": "2022-07-01"}),
                    ),
                )
            ],
        )
    )

    create_request = next(
        request
        for request in requests_mock.request_history
        if request.method == "POST" and urlparse(request.url).path.endswith("/logrequests")
    )
    assert parse_qs(urlparse(create_request.url).query)["fields"] == _load_raw_schema_fields("sessions.json")


@freezegun.freeze_time("2023-01-02")
def test_check_connection_no_end_date(config):
    config.pop("end_date")
    assert SourceYandexMetrica().get_end_date(config=config) == "2023-01-01"


def test_check_connection_incorrect_date(config_wrong_date):
    with pytest.raises(Exception):
        SourceYandexMetrica().check_connection(logger, config=config_wrong_date)
