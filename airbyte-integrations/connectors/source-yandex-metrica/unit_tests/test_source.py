#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from source_yandex_metrica.enums import YMCursor
from source_yandex_metrica.source import SourceYandexMetrica

logger = logging.getLogger("test_source")


@pytest.fixture
def fixtures():
    return {
        "config": {
            "auth_token": "test_token",
            "counter_id": "00000000",
            "start_date": "2022-07-01",
            "end_date": "2022-07-02",
            "hits_fields": ["watchID", "dateTime", "counterID"],
            "visits_fields": ["visitID", "dateTime", "counterID"],
            "check_connectivity": True,
        }
    }


def test_streams():
    source = SourceYandexMetrica()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2

    assert len(streams) == expected_streams_number


def test_check_connection_empty_config():
    config = {}
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_no_required_fields_1(fixtures):
    config = fixtures["config"]
    config["hits_fields"].remove(YMCursor.VIEWS)
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_no_required_fields_2(fixtures):
    config = fixtures["config"]
    config["visits_fields"].remove(YMCursor.SESSIONS)
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_invalid_fields_1(fixtures):
    config = fixtures["config"]
    config["hits_fields"].append("invalid_field")
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_invalid_fields_2(fixtures):
    config = fixtures["config"]
    config["visits_fields"].append("invalid_field")
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_invalid_api_key(fixtures):
    config = fixtures["config"]
    config["auth_token"] = "invalid_token"
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)

    assert not ok and error_msg
