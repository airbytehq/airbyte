#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi


def test_check_connection(mocker):
    source = SourceGoogleAnalyticsDataApi()

    report_mock = MagicMock()
    mocker.patch.object(SourceGoogleAnalyticsDataApi, "_run_report", return_value=report_mock)

    logger_mock = MagicMock()
    config_mock = MagicMock()

    assert source.check(logger_mock, config_mock) == AirbyteConnectionStatus(status=Status.SUCCEEDED)


def test_discover(mocker):
    source = SourceGoogleAnalyticsDataApi()

    dimensions_header_mock = MagicMock()
    dimensions_header_mock.name = "dimensions"

    metrics_header_mock = MagicMock()
    metrics_header_mock.name = "metrics"

    report_mock = MagicMock(dimension_headers=[dimensions_header_mock], metric_headers=[metrics_header_mock])
    mocker.patch.object(SourceGoogleAnalyticsDataApi, "_run_report", return_value=report_mock)

    logger_mock = MagicMock()
    config_mock = {"report_name": "test"}

    catalog = source.discover(logger_mock, config_mock)
    expected_streams_number = 1
    assert len(catalog.streams) == expected_streams_number
