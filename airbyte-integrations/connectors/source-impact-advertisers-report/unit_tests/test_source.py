#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import responses

from source_impact_advertisers_report.source import SourceImpactAdvertisersReport

DEFAULT_CONFIG = {
  "account_sid": "account_sid",
  "auth_token": "some_token",
  "report_id": "att_adv_performance_by_media_pm_only",
  "start_date": "2019-11-14",
  "sub_ad_id": "10732"
}

def setup_responses():
    responses.add(
        responses.GET,
        "https://api.impact.com/Advertisers/account_sid/CompanyInformation",
        json={"CompanyName": "My Company"},
    )


@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceImpactAdvertisersReport()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, DEFAULT_CONFIG) == (True, None)


def test_streams(mocker):
    source = SourceImpactAdvertisersReport()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
