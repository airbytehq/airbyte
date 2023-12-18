#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_outbrain_amplify.source import SourceOutbrainAmplify


def test_check_connection(mocker):
    config = {
        "credentials": {"type": "access_token", "access_token": "MTY1OTUyO"},
        "report_granularity": "daily",
        "geo_location_breakdown": "region",
        "start_date": "2022-04-01",
        "end_date": "2022-04-30",
    }
    source = SourceOutbrainAmplify()
    cond = source.check_connection(True, config)[0]
    assert cond is False


def test_streams(mocker):
    source = SourceOutbrainAmplify()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 17
    assert len(streams) == expected_streams_number
