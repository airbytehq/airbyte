#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi

json_credentials = """
{
    "type": "service_account",
    "project_id": "unittest-project-id",
    "private_key_id": "9qf98e52oda52g5ne23al6evnf13649c2u077162c",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEA3slcXL+dA36ESmOi\\n1xBhZmp5Hn0WkaHDtW4naba3plva0ibloBNWhFhjQOh7Ff01PVjhT4D5jgqXBIgc\\nz9Gv3QIDAQABAkEArlhYPoD5SB2/O1PjwHgiMPrL1C9B9S/pr1cH4vPJnpY3VKE3\\n5hvdil14YwRrcbmIxMkK2iRLi9lM4mJmdWPy4QIhAPsRFXZSGx0TZsDxD9V0ZJmZ\\n0AuDCj/NF1xB5KPLmp7pAiEA4yoFox6w7ql/a1pUVaLt0NJkDfE+22pxYGNQaiXU\\nuNUCIQCsFLaIJZiN4jlgbxlyLVeya9lLuqIwvqqPQl6q4ad12QIgS9gG48xmdHig\\n8z3IdIMedZ8ZCtKmEun6Cp1+BsK0wDUCIF0nHfSuU+eTQ2qAON2SHIrJf8UeFO7N\\nzdTN1IwwQqjI\\n-----END PRIVATE KEY-----\\n",
    "client_email": "google-analytics-access@unittest-project-id.iam.gserviceaccount.com",
    "client_id": "213243192021686092537",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-analytics-access%40unittest-project-id.iam.gserviceaccount.com"
}
"""


@pytest.fixture
def patch_base_class():
    return {
        "config": {
            "property_id": "108176369",
            "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
            "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
        }
    }


@pytest.fixture
def config():
    return {
        "property_id": "108176369",
        "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
        "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
        "custom_reports": json.dumps([{
            "name": "report1",
            "dimensions": ["date", "country"],
            "metrics": ["totalUsers", "screenPageViews"]
        }]),
    }


@pytest.fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}
    return inner


def test_check(requests_mock, config_gen):
    requests_mock.register_uri("POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"})
    requests_mock.register_uri("GET", "https://analyticsdata.googleapis.com/v1beta/properties/108176369/metadata", json={
        "dimensions": [{"apiName": "date"}, {"apiName": "country"}, {"apiName": "language"}, {"apiName": "browser"}],
        "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}],
    })
    requests_mock.register_uri("POST", "https://analyticsdata.googleapis.com/v1beta/properties/108176369:runReport",
                               json={"dimensionHeaders": [{"name": "date"}, {"name": "country"}],
                                     "metricHeaders": [{"name": "totalUsers", "type": "s"},
                                                       {"name": "screenPageViews", "type": "m"}],
                                     "rows": []
                                     })

    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()

    assert source.check(logger, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert source.check(logger, config_gen(custom_reports=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert source.check(logger, config_gen(custom_reports="[]")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert source.check(logger, config_gen(custom_reports="invalid")) == AirbyteConnectionStatus(status=Status.FAILED, message="'custom_reports is not valid JSON'")
    assert source.check(logger, config_gen(custom_reports="{}")) == AirbyteConnectionStatus(status=Status.FAILED, message='"custom_reports: {} is not of type \'array\'"')
    assert source.check(logger, config_gen(custom_reports="[{}]")) == AirbyteConnectionStatus(status=Status.FAILED, message='"custom_reports.0: \'name\' is a required property"')
    assert source.check(logger, config_gen(custom_reports='[{"name": "name"}]')) == AirbyteConnectionStatus(status=Status.FAILED, message='"custom_reports.0: \'dimensions\' is a required property"')
    assert source.check(logger, config_gen(custom_reports='[{"name": "name", "dimensions": [], "metrics": []}]')) == AirbyteConnectionStatus(status=Status.FAILED, message="'custom_reports.0.dimensions: [] is too short'")
    assert source.check(logger, config_gen(custom_reports='[{"name": "daily_active_users", "dimensions": ["date"], "metrics": ["totalUsers"]}]')) == AirbyteConnectionStatus(status=Status.FAILED, message="'custom_reports: daily_active_users already exist as a default report(s).'")
    assert source.check(logger, config_gen(custom_reports='[{"name": "name", "dimensions": ["unknown"], "metrics": ["totalUsers"]}]')) == AirbyteConnectionStatus(status=Status.FAILED, message="'custom_reports: invalid dimension(s): unknown for the custom report: name'")
    assert source.check(logger, config_gen(custom_reports='[{"name": "name", "dimensions": ["date"], "metrics": ["unknown"]}]')) == AirbyteConnectionStatus(status=Status.FAILED, message="'custom_reports: invalid metric(s): unknown for the custom report: name'")
    assert source.check(logger, config_gen(custom_reports='[{"name": "cohort_report", "dimensions": ["cohort", "cohortNthDay"], "metrics": ["cohortActiveUsers"], "cohortSpec": {"cohorts": [{"dimension": "firstSessionDate", "dateRange": {"startDate": "2023-01-01", "endDate": "2023-01-01"}}], "cohortsRange": {"endOffset": 100}}}]')) == AirbyteConnectionStatus(status=Status.FAILED, message='"custom_reports.0.cohortSpec.cohortsRange: \'granularity\' is a required property"')
    assert source.check(logger, config_gen(custom_reports='[{"name": "pivot_report", "dateRanges": [{ "startDate": "2020-09-01", "endDate": "2020-09-15" }], "dimensions": ["browser", "country", "language"], "metrics": ["sessions"], "pivots": {}}]')) == AirbyteConnectionStatus(status=Status.FAILED, message='"custom_reports.0.pivots: {} is not of type \'null\', \'array\'"')
    assert source.check(logger, config_gen(credentials={"auth_type": "Service", "credentials_json": "invalid"})) == AirbyteConnectionStatus(status=Status.FAILED, message="'credentials.credentials_json is not valid JSON'")
    assert source.check(logger, config_gen(date_ranges_start_date="2022-20-20")) == AirbyteConnectionStatus(status=Status.FAILED, message='"time data \'2022-20-20\' does not match format \'%Y-%m-%d\'"')


def test_streams(mocker, patch_base_class):
    source = SourceGoogleAnalyticsDataApi()

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"].__getitem__

    streams = source.streams(patch_base_class["config"])
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
