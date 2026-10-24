#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest
from source_yandex_metrica.source import SourceYandexMetrica
from source_yandex_metrica.streams import Sessions

from airbyte_cdk.models import SyncMode


logger = logging.getLogger("test_source")
EVALUATE_URL = "https://api-metrica.yandex.net/management/v1/counter/00000000/logrequests/evaluate"


def test_streams(config):
    source = SourceYandexMetrica()
    streams = source.streams(config)
    assert len(streams) == 2


def test_check_connection_success(config, requests_mock):
    requests_mock.get(
        EVALUATE_URL,
        [
            {"json": {"log_request_evaluation": {"possible": True}}},
            {"json": {"log_request_evaluation": {"possible": True}}},
        ],
    )
    streams = SourceYandexMetrica().streams(config.copy())

    assert SourceYandexMetrica().check_connection(logger, config=config) == (True, None)
    assert len(requests_mock.request_history) == 2
    for request, stream, source in zip(requests_mock.request_history, streams, ("visits", "hits")):
        assert request.headers["Authorization"] == "Bearer test_token"
        assert request.headers["Content-Type"] == "application/x-ymetrika+json"
        assert parse_qs(urlparse(request.url).query) == {
            "date1": ["2022-07-01"],
            "date2": ["2022-07-02"],
            "source": [source],
            "fields": stream.get_request_fields(),
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
        "fields": stream.get_request_fields(),
    }


@freezegun.freeze_time("2023-01-02")
def test_check_connection_no_end_date(config):
    config.pop("end_date")
    assert SourceYandexMetrica().get_end_date(config=config) == "2023-01-01"


def test_check_connection_incorrect_date(config_wrong_date):
    with pytest.raises(Exception):
        SourceYandexMetrica().check_connection(logger, config=config_wrong_date)
