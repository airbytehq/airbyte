#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_outbrain_amplify.source import SourceOutbrainAmplify
from source_outbrain_amplify.auth import OutbrainAmplifyAuthenticator


def test_check_connection(mocker):
    config = { "credentials":
                {
                    "type": "access_token",
                    "access_token" : "MTY1OTUyO"
                },
                "report_granularity": "daily",
                "geo_location_breakdown": "region",
                "start_date" : "2022-04-01",
                "end_date" : "2022-04-30"
            }
    source = SourceOutbrainAmplify()
    assert source.check_connection(True, config)[0] == False


def test_streams(mocker):
    source = SourceOutbrainAmplify()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 17
    assert len(streams) == expected_streams_number
