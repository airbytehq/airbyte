#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, FailureType, Status
from airbyte_cdk.utils import AirbyteTracedException
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi
from source_google_analytics_data_api.utils import NO_DIMENSIONS, NO_METRICS, NO_NAME, WRONG_JSON_SYNTAX

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


@pytest.mark.parametrize(
    "config_values, status, message",
    [
        ({}, Status.SUCCEEDED, None),
        ({"custom_reports": ...}, Status.SUCCEEDED, None),
        ({"custom_reports": "[]"}, Status.SUCCEEDED, None),
        ({"custom_reports": "invalid"}, Status.FAILED, f"'{WRONG_JSON_SYNTAX}'"),
        ({"custom_reports": "{}"}, Status.FAILED, f"'{WRONG_JSON_SYNTAX}'"),
        ({"custom_reports": "[{}]"}, Status.FAILED, f"'{NO_NAME}'"),
        ({"custom_reports": "[{\"name\": \"name\"}]"}, Status.FAILED, f"'{NO_DIMENSIONS}'"),
        ({"custom_reports": "[{\"name\": \"daily_active_users\", \"dimensions\": [\"date\"]}]"}, Status.FAILED, f"'{NO_METRICS}'"),
        ({"custom_reports": "[{\"name\": \"daily_active_users\", \"metrics\": [\"totalUsers\"], \"dimensions\": [{\"name\": \"city\"}]}]"}, Status.FAILED, '"The custom report daily_active_users entered contains invalid dimensions: {\'name\': \'city\'} is not of type \'string\'. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/)."'),
        ({"date_ranges_start_date": "2022-20-20"}, Status.FAILED, '"time data \'2022-20-20\' does not match format \'%Y-%m-%d\'"'),
        ({"credentials": {"auth_type": "Service", "credentials_json": "invalid"}},
         Status.FAILED, "'credentials.credentials_json is not valid JSON'"),
        ({"custom_reports": "[{\"name\": \"name\", \"dimensions\": [], \"metrics\": []}]"}, Status.FAILED, "'The custom report name entered contains invalid dimensions: [] is too short. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'"),
        ({"custom_reports": "[{\"name\": \"daily_active_users\", \"dimensions\": [\"date\"], \"metrics\": [\"totalUsers\"]}]"}, Status.FAILED, "'custom_reports: daily_active_users already exist as a default report(s).'"),
        ({"custom_reports": "[{\"name\": \"name\", \"dimensions\": [\"unknown\"], \"metrics\": [\"totalUsers\"]}]"},
         Status.FAILED, "'The custom report name entered contains invalid dimensions: unknown. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'"),
        ({"custom_reports": "[{\"name\": \"name\", \"dimensions\": [\"date\"], \"metrics\": [\"unknown\"]}]"}, Status.FAILED, "'The custom report name entered contains invalid metrics: unknown. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'"),
        ({"custom_reports": "[{\"name\": \"cohort_report\", \"dimensions\": [\"cohort\", \"cohortNthDay\"], \"metrics\": "
                            "[\"cohortActiveUsers\"], \"cohortSpec\": {\"cohorts\": [{\"dimension\": \"firstSessionDate\", \"dateRange\": "
                            "{\"startDate\": \"2023-01-01\", \"endDate\": \"2023-01-01\"}}], \"cohortsRange\": {\"endOffset\": 100}}}]"},
         Status.FAILED, '"custom_reports.0.cohortSpec.cohortsRange: \'granularity\' is a required property"'),
        ({"custom_reports": "[{\"name\": \"pivot_report\", \"dateRanges\": [{ \"startDate\": \"2020-09-01\", \"endDate\": "
                            "\"2020-09-15\" }], \"dimensions\": [\"browser\", \"country\", \"language\"], \"metrics\": [\"sessions\"], "
                            "\"pivots\": {}}]"},
         Status.FAILED, '"The custom report pivot_report entered contains invalid pivots: {} is not of type \'null\', \'array\'. Ensure the pivot follow the syntax described in the docs (https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot)."'),
    ],
)
def test_check(requests_mock, config_gen, config_values, status, message):
    requests_mock.register_uri("POST", "https://oauth2.googleapis.com/token",
                               json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"})

    requests_mock.register_uri("GET", "https://analyticsdata.googleapis.com/v1beta/properties/108176369/metadata",
                               json={"dimensions": [{"apiName": "date"}, {"apiName": "country"},
                                                    {"apiName": "language"}, {"apiName": "browser"}],
                                     "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}]})
    requests_mock.register_uri("POST", "https://analyticsdata.googleapis.com/v1beta/properties/108176369:runReport",
                               json={"dimensionHeaders": [{"name": "date"}, {"name": "country"}],
                                     "metricHeaders": [{"name": "totalUsers", "type": "s"},
                                                       {"name": "screenPageViews", "type": "m"}],
                                     "rows": []
                                     })
    requests_mock.register_uri("GET", "https://analyticsdata.googleapis.com/v1beta/properties/UA-11111111/metadata",
                               json={}, status_code=403)

    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    assert source.check(logger, config_gen(**config_values)) == AirbyteConnectionStatus(status=status, message=message)

    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger, config_gen(property_id="UA-11111111"))
    assert e.value.failure_type == FailureType.config_error


def test_streams(mocker, patch_base_class):
    source = SourceGoogleAnalyticsDataApi()

    config_mock = MagicMock()
    config_mock.__getitem__.side_effect = patch_base_class["config"].__getitem__

    streams = source.streams(patch_base_class["config"])
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
