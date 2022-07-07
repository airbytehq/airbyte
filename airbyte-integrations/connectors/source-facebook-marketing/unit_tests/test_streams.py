#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from pendulum import duration
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.base_streams import FBMarketingStream
from source_facebook_marketing.streams.streams import fetch_thumbnail_data_url


def test_filter_all_statuses(api, mocker):
    mocker.patch.multiple(FBMarketingStream, __abstractmethods__=set())
    expected = {
        "filtering": [
            {
                "field": "None.delivery_info",
                "operator": "IN",
                "value": [
                    "active",
                    "archived",
                    "completed",
                    "limited",
                    "not_delivering",
                    "deleted",
                    "not_published",
                    "pending_review",
                    "permanently_deleted",
                    "recently_completed",
                    "recently_rejected",
                    "rejected",
                    "scheduled",
                    "inactive",
                ],
            }
        ]
    }
    assert FBMarketingStream(api=api)._filter_all_statuses() == expected


@pytest.mark.parametrize(
    "url", ["https://graph.facebook.com", "https://graph.facebook.com?test=123%23%24%25%2A&test2=456", "https://graph.facebook.com?"]
)
def test_fetch_thumbnail_data_url(url, requests_mock):
    requests_mock.get(url, status_code=200, headers={"content-type": "content-type"}, content=b"")
    assert fetch_thumbnail_data_url(url) == "data:content-type;base64,"


def test_parse_call_rate_header():
    headers = {
        "x-business-use-case-usage": '{"test":[{"type":"ads_management","call_count":1,"total_cputime":1,'
        '"total_time":1,"estimated_time_to_regain_access":1}]}'
    }
    assert MyFacebookAdsApi._parse_call_rate_header(headers) == (1, duration(minutes=1))
