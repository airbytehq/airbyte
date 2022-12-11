#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status
from source_shortio.source import SourceShortio


@pytest.fixture
def config():
    return {"domain_id": "foo", "secret_key": "bar", "start_date": "2030-01-01"}


def test_source_shortio_client_wrong_credentials():
    source = SourceShortio()
    result = source.check(logger=AirbyteLogger, config={"domain_id": "foo", "secret_key": "bar", "start_date": "2030-01-01"})
    assert result.status == Status.FAILED


def test_streams():
    source = SourceShortio()
    config_mock = {"domain_id": "foo", "secret_key": "bar", "start_date": "2030-01-01"}
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
