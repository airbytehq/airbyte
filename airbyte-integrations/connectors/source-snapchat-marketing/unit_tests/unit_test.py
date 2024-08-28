#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from conftest import find_stream
from source_snapchat_marketing.source import SourceSnapchatMarketing

logger = logging.getLogger("airbyte_logger")

config_mock = {
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
    "start_date": "2024-01-01",
    "end_date": "2024-02-10",
    "action_report_time": "impression",
    "swipe_up_attribution_window": "7_DAY",
    "view_attribution_window": "1_DAY",
}

response_organizations = {
    "organizations": [
        {
            "organization": {
                "id": "organization_id_1",
                "updated_at": "2024-02-05T22:35:17.819Z",
                "created_at": "2024-02-05T11:13:03.910Z",
            }
        }
    ]
}


def test_should_retry_403_error(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})
    requests_mock.register_uri(
        "GET", "https://adsapi.snapchat.com/v1/me/organizations", [{"status_code": 403, "json": {"organizations": []}}]
    )
    stream = find_stream("organizations", config_mock)
    # make a single retry to save time
    stream.retriever.requester.error_handler.max_retries = 1
    
    with pytest.raises(UserDefinedBackoffException):
        list(stream.read_records(sync_mode=SyncMode.full_refresh))


def test_organizations(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})
    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    stream = find_stream("organizations", config_mock)
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=StreamSlice(partition={},
                                                                                            cursor_slice={"start_time": "2024-01-01",
                                                                                                          "end_time": "2024-01-01"}),
                                  stream_state=None)
    assert json.dumps(next(records).data, sort_keys=True) == json.dumps(
        {"id": "organization_id_1", "updated_at": "2024-02-05T22:35:17.819Z", "created_at": "2024-02-05T11:13:03.910Z"}, sort_keys=True)


response_adaccounts = {
    "adaccounts": [
        {
            "adaccount": {
                "id": "adaccount_id_1",
                "updated_at": "2024-02-05T22:35:17.819Z",
                "created_at": "2024-02-05T11:13:03.910Z",
            }
        },
        {
            "adaccount": {
                "id": "adaccount_id_2",
                "updated_at": "2024-02-05T22:35:17.819Z",
                "created_at": "2024-02-05T11:13:03.910Z",
            }
        },
    ]
}


def run_stream(stream):
    slices = stream.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        yield from stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)


def test_accounts(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)

    stream = find_stream("adaccounts", config_mock)
    records = run_stream(stream)
    list_records = [record.data for record in records]
    assert list_records == [
        {
            "id": "adaccount_id_1",
            "updated_at": "2024-02-05T22:35:17.819Z",
            "created_at": "2024-02-05T11:13:03.910Z",
        },
        {
            "id": "adaccount_id_2",
            "updated_at": "2024-02-05T22:35:17.819Z",
            "created_at": "2024-02-05T11:13:03.910Z",
        },
    ]


response_ads = {
    "ads": [
        {
            "ad": {
                "id": "ad_id_1",
                "updated_at": "2024-02-05T22:35:17.819Z",
                "created_at": "2024-02-05T11:13:03.910Z",
            }
        },
        {
            "ad": {
                "id": "ad_id_2",
                "updated_at": "2024-02-05T22:35:17.819Z",
                "created_at": "2024-02-05T11:13:03.910Z",
            }
        },
    ]
}


def test_ads(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)

    stream = find_stream("ads", config_mock)
    records = run_stream(stream)
    list_records = [record.data for record in records]
    assert list_records == [
        {
            "id": "ad_id_1",
            "updated_at": "2024-02-05T22:35:17.819Z",
            "created_at": "2024-02-05T11:13:03.910Z",
        },
        {
            "id": "ad_id_2",
            "updated_at": "2024-02-05T22:35:17.819Z",
            "created_at": "2024-02-05T11:13:03.910Z",
        },
    ]


response_ads_stats_lifetime_1 = {
    "request_status": "SUCCESS",
    "request_id": "d0cb395f-c39d-480d-b62c-24878c7d0b76",
    "lifetime_stats": [
        {
            "sub_request_status": "SUCCESS",
            "lifetime_stat": {
                "id": "ad_id_1",
                "type": "AD",
                "granularity": "LIFETIME",
                "stats": {
                    "impressions": 0,
                    "swipes": 0,
                    "spend": 1,
                },
                "start_time": "2016-09-26T00:00:00.000-07:00",
                "end_time": "2022-07-01T07:00:00.000-07:00",
                "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
                "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            },
        }
    ],
}

response_ads_stats_lifetime_2 = {
    "request_status": "SUCCESS",
    "request_id": "d0cb395f-c39d-480d-b62c-24878c7d0b76",
    "lifetime_stats": [
        {
            "sub_request_status": "SUCCESS",
            "lifetime_stat": {
                "id": "ad_id_2",
                "type": "AD",
                "granularity": "LIFETIME",
                "stats": {
                    "impressions": 0,
                    "swipes": 0,
                    "spend": 2,
                },
                "start_time": "2016-09-26T00:00:00.000-07:00",
                "end_time": "2022-07-01T07:00:00.000-07:00",
                "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
                "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            },
        }
    ],
}


def test_ads_stats_lifetime(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_1/stats", json=response_ads_stats_lifetime_1)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_2/stats", json=response_ads_stats_lifetime_2)

    stream = find_stream("ads_stats_lifetime", config_mock)
    records = run_stream(stream)
    list_records = [record.data for record in records]
    assert list_records == [
        {
            "id": "ad_id_1",
            "type": "AD",
            "granularity": "LIFETIME",
            "start_time": "2016-09-26T00:00:00.000-07:00",
            "end_time": "2022-07-01T07:00:00.000-07:00",
            "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
            "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            "android_installs": None,
            "attachment_avg_view_time_millis": None,
            "attachment_impressions": None,
            "attachment_quartile_1": None,
            "attachment_quartile_2": None,
            "attachment_quartile_3": None,
            "attachment_total_view_time_millis": None,
            "attachment_view_completion": None,
            "avg_screen_time_millis": None,
            "avg_view_time_millis": None,
            "impressions": 0,
            "ios_installs": None,
            "quartile_1": None,
            "quartile_2": None,
            "quartile_3": None,
            "screen_time_millis": None,
            "swipe_up_percent": None,
            "swipes": 0,
            "spend": 1,
            "total_installs": None,
            "video_views": None,
            "video_views_time_based": None,
            "video_views_15s": None,
            "view_completion": None,
            "view_time_millis": None,
            "paid_impressions": None,
            "earned_impressions": None,
            "total_impressions": None,
            "play_time_millis": None,
            "shares": None,
            "saves": None,
            "native_leads": None,
            "conversion_purchases": None,
            "conversion_purchases_value": None,
            "conversion_save": None,
            "conversion_start_checkout": None,
            "conversion_add_cart": None,
            "conversion_view_content": None,
            "conversion_add_billing": None,
            "conversion_searches": None,
            "conversion_level_completes": None,
            "conversion_app_opens": None,
            "conversion_page_views": None,
            "conversion_subscribe": None,
            "conversion_ad_click": None,
            "conversion_ad_view": None,
            "conversion_complete_tutorial": None,
            "conversion_invite": None,
            "conversion_login": None,
            "conversion_share": None,
            "conversion_reserve": None,
            "conversion_achievement_unlocked": None,
            "conversion_add_to_wishlist": None,
            "conversion_spend_credits": None,
            "conversion_rate": None,
            "conversion_start_trial": None,
            "conversion_list_view": None,
            "custom_event_1": None,
            "custom_event_2": None,
            "custom_event_3": None,
            "custom_event_4": None,
            "custom_event_5": None,
            "story_opens": None,
            "story_completes": None,
            "attachment_frequency": None,
            "attachment_uniques": None,
            "frequency": None,
            "uniques": None,
            "total_reach": None,
            "earned_reach": None
        },
        {
            "id": "ad_id_2",
            "type": "AD",
            "granularity": "LIFETIME",
            "start_time": "2016-09-26T00:00:00.000-07:00",
            "end_time": "2022-07-01T07:00:00.000-07:00",
            "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
            "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            "android_installs": None,
            "attachment_avg_view_time_millis": None,
            "attachment_impressions": None,
            "attachment_quartile_1": None,
            "attachment_quartile_2": None,
            "attachment_quartile_3": None,
            "attachment_total_view_time_millis": None,
            "attachment_view_completion": None,
            "avg_screen_time_millis": None,
            "avg_view_time_millis": None,
            "impressions": 0,
            "ios_installs": None,
            "quartile_1": None,
            "quartile_2": None,
            "quartile_3": None,
            "screen_time_millis": None,
            "swipe_up_percent": None,
            "swipes": 0,
            "spend": 2,
            "total_installs": None,
            "video_views": None,
            "video_views_time_based": None,
            "video_views_15s": None,
            "view_completion": None,
            "view_time_millis": None,
            "paid_impressions": None,
            "earned_impressions": None,
            "total_impressions": None,
            "play_time_millis": None,
            "shares": None,
            "saves": None,
            "native_leads": None,
            "conversion_purchases": None,
            "conversion_purchases_value": None,
            "conversion_save": None,
            "conversion_start_checkout": None,
            "conversion_add_cart": None,
            "conversion_view_content": None,
            "conversion_add_billing": None,
            "conversion_searches": None,
            "conversion_level_completes": None,
            "conversion_app_opens": None,
            "conversion_page_views": None,
            "conversion_subscribe": None,
            "conversion_ad_click": None,
            "conversion_ad_view": None,
            "conversion_complete_tutorial": None,
            "conversion_invite": None,
            "conversion_login": None,
            "conversion_share": None,
            "conversion_reserve": None,
            "conversion_achievement_unlocked": None,
            "conversion_add_to_wishlist": None,
            "conversion_spend_credits": None,
            "conversion_rate": None,
            "conversion_start_trial": None,
            "conversion_list_view": None,
            "custom_event_1": None,
            "custom_event_2": None,
            "custom_event_3": None,
            "custom_event_4": None,
            "custom_event_5": None,
            "story_opens": None,
            "story_completes": None,
            "attachment_frequency": None,
            "attachment_uniques": None,
            "frequency": None,
            "uniques": None,
            "total_reach": None,
            "earned_reach": None
        }
    ]


response_ads_stats_daily_1 = {
    "request_status": "SUCCESS",
    "request_id": "f2cba857-e246-43bf-b644-1a0a540e1f92",
    "timeseries_stats": [
        {
            "sub_request_status": "SUCCESS",
            "timeseries_stat": {
                "id": "417d0269-80fb-496a-b5f3-ec0bac665144",
                "type": "AD",
                "granularity": "DAY",
                "start_time": "2024-02-05T00:00:00.000-07:00",
                "end_time": "2024-02-08T00:00:00.000-07:00",
                "finalized_data_end_time": "2022-06-30T00:00:00.000-07:00",
                "conversion_data_processed_end_time": "2022-06-30T00:00:00.000Z",
                "timeseries": [
                    {
                        "start_time": "2024-02-05T00:00:00.000-07:00",
                        "end_time": "2024-02-06T00:00:00.000-07:00",
                        "stats": {
                            "impressions": 0,
                            "swipes": 0,
                            "quartile_1": 0,
                            "quartile_2": 0,
                            "quartile_3": 0,
                        },
                    },
                    {
                        "start_time": "2024-02-07T00:00:00.000-07:00",
                        "end_time": "2024-02-08T00:00:00.000-07:00",
                        "stats": {
                            "impressions": 0,
                            "swipes": 0,
                            "quartile_1": 0,
                            "quartile_2": 0,
                            "quartile_3": 0,
                        },
                    },
                ],
            },
        }
    ],
}


def test_ads_stats_daily(requests_mock):
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_1/stats", json={"timeseries_stats": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_2/stats", json=response_ads_stats_daily_1)

    stream = find_stream("ads_stats_daily", config_mock)
    records = run_stream(stream)
    assert len(list(records)) == 4  # 2 records for each of 2 slices


def test_source_streams():
    source_config = {"client_id": "XXX", "client_secret": "XXX", "refresh_token": "XXX", "start_date": "2022-05-25"}
    streams = SourceSnapchatMarketing().streams(config=source_config)
    assert len(streams) == 20


def test_source_check_connection(requests_mock):
    source_config = {"client_id": "XXX", "client_secret": "XXX", "refresh_token": "XXX", "start_date": "2022-05-25"}
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})
    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json={})

    results = SourceSnapchatMarketing().check_connection(logger=logger, config=source_config)
    assert results == (True, None)
