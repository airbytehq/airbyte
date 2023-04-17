#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config
from source_criteo.source import SourceCriteo

configuration = {
    "advertiserIds": "10817,10398",
    "authorization": {
        "auth_type": "Client",
        "client_id": "Z0xHZlAJ1VMmNW2mbc3WXsW4nMIlL9q8",
        "client_secret": "WY4SghQcVYJWHo8BLTmtW7xHX5J33le4jrRvnc2kAEW7",
    },
    "start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
    "end_date": datetime.datetime.strftime((datetime.datetime.now()), "%Y-%m-%d"),
    "dimensions": ["AdvertiserId", "Os", "Day"],
    "metrics": ["Displays", "Clicks"],
    "currency": "EUR",
    "timezone": "Europe/Rome",
    "lookback_window": 1,
}


@pytest.fixture
def patch_base_class():
    return {"config": configuration}


@pytest.fixture
def config():
    return configuration


def command_check(logger, source: Source, config):
    connector_config, _ = split_config(config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)


@pytest.fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner


def test_check(requests_mock, config_gen):
    requests_mock.register_uri(
        "POST", "https://api.criteo.com/oauth2/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )

    requests_mock.register_uri(
        "POST",
        "https://api.criteo.com/2023-01/statistics/report",
        json={
            "advertiserIds": "10817,10398",
            "startDate": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
            "endDate": datetime.datetime.strftime((datetime.datetime.now()), "%Y-%m-%d"),
            "format": "json",
            "dimensions": ["AdvertiserId", "Os", "Day"],
            "metrics": ["Displays", "Clicks"],
            "timezone": "Europe/Rome",
            "currency": "EUR",
        },
    )

    source = SourceCriteo()
    logger = MagicMock()
    assert command_check(logger, source, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    with pytest.raises(Exception):
        assert command_check(logger, source, config_gen(dimensions=["OS"]))

    with pytest.raises(Exception):
        assert command_check(logger, config_gen(metrics=["Display"]))

    assert command_check(logger, source, config_gen(start_date="2023-20-20")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to connect to Criteo API with the provided credentials - ParserError('Unable to parse string [2023-20-20]')\"",
    )


def test_streams(mocker, patch_base_class):
    source = SourceCriteo()

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"].__getitem__

    streams = source.streams(patch_base_class["config"])
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
