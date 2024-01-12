#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from samples.test_data_for_analytics import test_output_slices
from source_linkedin_ads.analytics_streams import AdMemberCountryAnalytics

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

def test_analytics_stream_slices(requests_mock):
    requests_mock.get('https://api.linkedin.com/rest/adAccounts', json={"elements": [{"id": 1 }]})
    requests_mock.get('https://api.linkedin.com/rest/adAccounts/1/adCampaigns', json={"elements": [{"id": 123}]})
    assert list(AdMemberCountryAnalytics(config=TEST_CONFIG).stream_slices(sync_mode=None,)) == test_output_slices
