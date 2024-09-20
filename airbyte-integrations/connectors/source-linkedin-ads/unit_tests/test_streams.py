#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from conftest import find_stream
from freezegun import freeze_time

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


# HELPERS
def load_json_file(file_name: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/{file_name}", "r") as data:
        return json.load(data)


@freeze_time("2021-03-01")
def test_analytics_stream_slices(requests_mock):
    stream = find_stream("ad_member_country_analytics", TEST_CONFIG)
    requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
    requests_mock.get("https://api.linkedin.com/rest/adAccounts/1/adCampaigns", json={"elements": [{"id": 123}]})
    assert [dict(i) for i in list(stream.retriever.stream_slicer.stream_slices())] == load_json_file("output_slices.json")


def test_read_records(requests_mock):
    stream = find_stream("ad_member_country_analytics", TEST_CONFIG)
    requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
    requests_mock.get(
        "https://api.linkedin.com/rest/adAccounts/1/adCampaigns?q=search&search=(status:(values:List(ACTIVE,PAUSED,ARCHIVED,COMPLETED,CANCELED,DRAFT,PENDING_DELETION,REMOVED)))",
        json={"elements": [{"id": 1111, "lastModified": "2021-01-15"}]})
    requests_mock.get(
        "https://api.linkedin.com/rest/adAnalytics",
        [
            {"json": load_json_file("responses/ad_member_country_analytics/response_1.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_2.json")},
            {"json": load_json_file("responses/ad_member_country_analytics/response_3.json")},
        ],
    )

    stream_slice = next(stream.stream_slices(sync_mode=SyncMode.incremental))
    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice, stream_state=None))
    assert len(records) == 2
