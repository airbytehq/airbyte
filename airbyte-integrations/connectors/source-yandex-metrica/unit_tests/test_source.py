#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import freezegun
import pytest
from source_yandex_metrica.source import SourceYandexMetrica


logger = logging.getLogger("test_source")


def test_streams(config):
    source = SourceYandexMetrica()
    streams = source.streams(config)
    assert len(streams) == 2


def test_check_connection_invalid_api_key(config, requests_mock):
    config["auth_token"] = "invalid_token"
    requests_mock.register_uri(
        "GET", "https://api-metrica.yandex.net/management/v1/counter/00000000/logrequests/evaluate", [{"status_code": 400}]
    )
    ok, error_msg = SourceYandexMetrica().check_connection(logger, config=config)
    assert not ok and error_msg


@freezegun.freeze_time("2023-01-02")
def test_check_connection_no_end_date(config):
    config.pop("end_date")
    assert SourceYandexMetrica().get_end_date(config=config) == "2023-01-01"


def test_check_connection_incorrect_date(config_wrong_date):
    with pytest.raises(Exception):
        SourceYandexMetrica().check_connection(logger, config=config_wrong_date)
