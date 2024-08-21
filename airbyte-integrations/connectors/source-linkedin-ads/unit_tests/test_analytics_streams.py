#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_linkedin_ads.analytics_streams import AdMemberCountryAnalytics, LinkedInAdsAnalyticsStream

# Test input arguments for the `make_analytics_slices`
TEST_KEY_VALUE_MAP = {"camp_id": "id"}
TEST_START_DATE = "2021-08-01"
TEST_END_DATE = "2021-09-30"

# This is the mock of the request_params
TEST_REQUEST_PRAMS = {}


TEST_CONFIG: dict = {
    "start_date": "2021-01-01",
    "end_date": "2021-02-01",
    "account_ids": [1, 2],
    "credentials": {
        "auth_method": "access_token",
        "access_token": "access_token",
        "authenticator": TokenAuthenticator(token="123"),
    },
}

# Test chunk size for each field set
TEST_FIELDS_CHUNK_SIZE = 3
# Test fields assuming they are really available for the fetch
TEST_ANALYTICS_FIELDS = [
    "field_1",
    "base_field_1",
    "field_2",
    "base_field_2",
    "field_3",
    "field_4",
    "field_5",
    "field_6",
    "field_7",
    "field_8",
]


# HELPERS
def load_json_file(file_name: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/{file_name}", "r") as data:
        return json.load(data)


def test_analytics_stream_slices(requests_mock):
    requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
    requests_mock.get("https://api.linkedin.com/rest/adAccounts/1/adCampaigns", json={"elements": [{"id": 123}]})
    assert list(
        AdMemberCountryAnalytics(config=TEST_CONFIG).stream_slices(
            sync_mode=None,
        )
    ) == load_json_file("output_slices.json")


def test_read_records(requests_mock):
    requests_mock.get(
        "https://api.linkedin.com/rest/adAnalytics",
        [
            {"json": load_json_file("responses/ad_member_country_analytics/response_1.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_2.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_3.json")},
        ],
    )
    stream_slice = load_json_file("output_slices.json")[0]
    records = list(AdMemberCountryAnalytics(config=TEST_CONFIG).read_records(stream_slice=stream_slice, sync_mode=None))
    assert len(records) == 2


def test_chunk_analytics_fields():
    """
    We expect to truncate the field list into the chunks of equal size,
    with "dateRange" field presented in each chunk.
    """
    expected_output = [
        ["field_1", "base_field_1", "field_2", "dateRange", "pivotValues"],
        ["base_field_2", "field_3", "field_4", "dateRange", "pivotValues"],
        ["field_5", "field_6", "field_7", "dateRange", "pivotValues"],
        ["field_8", "dateRange", "pivotValues"],
    ]

    assert list(LinkedInAdsAnalyticsStream.chunk_analytics_fields(TEST_ANALYTICS_FIELDS, TEST_FIELDS_CHUNK_SIZE)) == expected_output


def test_get_date_slices():
    """
    By default, we use the `WINDOW_SIZE = 30`, as it set in the analytics module
    This value could be changed by setting the corresponding argument in the method.
    The `end_date` is not specified by default, but for this test it was specified to have the test static.
    """

    test_start_date = "2021-08-01"
    test_end_date = "2021-10-01"

    expected_output = [
        {"dateRange": {"start.day": 1, "start.month": 8, "start.year": 2021, "end.day": 31, "end.month": 8, "end.year": 2021}},
        {"dateRange": {"start.day": 31, "start.month": 8, "start.year": 2021, "end.day": 30, "end.month": 9, "end.year": 2021}},
        {"dateRange": {"start.day": 30, "start.month": 9, "start.year": 2021, "end.day": 30, "end.month": 10, "end.year": 2021}},
    ]

    assert list(LinkedInAdsAnalyticsStream.get_date_slices(test_start_date, test_end_date)) == expected_output
