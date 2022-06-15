#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_my_hours.constants import URL_BASE
from source_my_hours.source import SourceMyHours, TimeLogs

DEFAULT_CONFIG = {"email": "john@doe.com", "password": "pwd"}


@responses.activate
def test_check_connection_success(mocker):
    source = SourceMyHours()
    logger_mock = MagicMock()

    responses.add(responses.POST, f"{URL_BASE}/tokens/login", json={"accessToken": "at", "refreshToken": "rt", "expiresIn": 100})
    responses.add(
        responses.GET,
        f"{URL_BASE}/Clients",
    )

    assert source.check_connection(logger_mock, DEFAULT_CONFIG) == (True, None)


@responses.activate
def test_check_connection_authentication_failure(mocker):
    source = SourceMyHours()
    logger_mock = MagicMock()

    responses.add(responses.POST, f"{URL_BASE}/tokens/login", status=403, json={"message": "Incorrect email or password"})

    success, exception = source.check_connection(logger_mock, DEFAULT_CONFIG)

    assert success is False
    assert exception is not None


@responses.activate
def test_check_connection_connection_failure(mocker):
    source = SourceMyHours()
    logger_mock = MagicMock()

    responses.add(responses.POST, f"{URL_BASE}/tokens/login", json={"accessToken": "at", "refreshToken": "rt", "expiresIn": 100})
    responses.add(responses.GET, f"{URL_BASE}/Clients", status=403)

    success, exception = source.check_connection(logger_mock, DEFAULT_CONFIG)
    assert success is False
    assert exception is not None


@responses.activate
def test_streams(mocker):
    source = SourceMyHours()
    responses.add(responses.POST, f"{URL_BASE}/tokens/login", json={"accessToken": "at", "refreshToken": "rt", "expiresIn": 100})
    config = {"email": "john@doe.com", "password": "pwd", "logs_batch_size": 30, "start_date": "2021-01-01"}

    streams = source.streams(config)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


def test_time_logs_next_page_token(mocker):
    stream = TimeLogs(authenticator=MagicMock(), start_date="2021-01-01", batch_size=10)
    reponse_mock = MagicMock()
    reponse_mock.request.url = "https://myhours.com/test?DateTo=2021-01-01"
    inputs = {"response": reponse_mock}
    expected_token = {"DateFrom": "2021-01-02", "DateTo": "2021-01-11"}
    assert stream.next_page_token(**inputs) == expected_token
