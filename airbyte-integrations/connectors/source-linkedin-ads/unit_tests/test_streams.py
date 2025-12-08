#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from freezegun import freeze_time

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .conftest import find_stream, load_json_file


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


@freeze_time("2021-03-01")
def test_analytics_stream_slices(requests_mock):
    expected_partitions = [
        {
            "campaign_id": 123,
            "start_time": "2021-01-01",
            "end_time": "2021-01-31",
            "parent_slice": {"account_id": 1, "parent_slice": {}},
        },
        {
            "campaign_id": 123,
            "start_time": "2021-01-31",
            "end_time": "2021-03-01",
            "parent_slice": {"account_id": 1, "parent_slice": {}},
        },
    ]

    stream = find_stream("ad_member_country_analytics", TEST_CONFIG)
    requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
    requests_mock.get("https://api.linkedin.com/rest/adAccounts/1/adCampaigns", json={"elements": [{"id": 123}]})
    assert [partition.to_slice() for partition in list(stream.generate_partitions())] == expected_partitions


def test_read_records(requests_mock):
    stream = find_stream("ad_member_country_analytics", TEST_CONFIG)
    requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
    requests_mock.get(
        "https://api.linkedin.com/rest/adAccounts/1/adCampaigns?q=search&search=(status:(values:List(ACTIVE,PAUSED,ARCHIVED,COMPLETED,CANCELED,DRAFT,PENDING_DELETION,REMOVED)))",
        json={"elements": [{"id": 1111, "lastModified": "2021-01-15"}]},
    )
    requests_mock.get(
        "https://api.linkedin.com/rest/adAnalytics",
        [
            {"json": load_json_file("responses/ad_member_country_analytics/response_1.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_2.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_3.json")},
        ],
    )

    partitions = iter(stream.generate_partitions())
    partition_1 = next(partitions)
    records = list(partition_1.read())

    assert len(records) == 2
