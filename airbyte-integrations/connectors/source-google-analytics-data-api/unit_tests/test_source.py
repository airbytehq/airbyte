#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.streams.http import HttpStream
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi

json_credentials = """
{
    "type": "service_account",
    "project_id": "unittest-project-id",
    "private_key_id": "9qf98e52oda52g5ne23al6evnf13649c2u077162c",
    "private_key": "",
    "client_email": "google-analytics-access@unittest-project-id.iam.gserviceaccount.com",
    "client_id": "213243192021686092537",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-analytics-access%40unittest-project-id.iam.gserviceaccount.com"
}
"""


@pytest.fixture
def patch_base_class(mocker):
    return {
        "config": {
            "property_id": "108176369",
            "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
            "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
        }
    }


def test_check_connection(mocker, patch_base_class):
    source = SourceGoogleAnalyticsDataApi()
    record = MagicMock()

    logger_mock, config_mock = MagicMock(), MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"].__getitem__

    mocker.patch.object(HttpStream, "read_records", return_value=[record])
    assert source.check(logger_mock, config_mock) == AirbyteConnectionStatus(status=Status.SUCCEEDED)


def test_streams(mocker, patch_base_class):
    source = SourceGoogleAnalyticsDataApi()

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"].__getitem__

    streams = source.streams(patch_base_class["config"])
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
