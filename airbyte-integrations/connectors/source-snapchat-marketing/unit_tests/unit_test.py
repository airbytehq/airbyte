#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# from unittest.mock import MagicMock, PropertyMock, patch

import pytest
import source_snapchat_marketing
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_snapchat_marketing.source import (
    Adaccounts,
    AdaccountsStatsDaily,
    Ads,
    AdsStatsDaily,
    AdsStatsLifetime,
    Organizations,
    SnapchatOauth2Authenticator,
    SourceSnapchatMarketing,
)

config_mock = {
    "authenticator": NoAuth(),
    "start_date": "2000-01-01",
    "end_date": "2000-02-10",
}
stats_stream = AdaccountsStatsDaily(**config_mock)


@pytest.mark.parametrize(
    "slice_period,expected_date_slices",
    [
        # for Hourly streams
        (
            7,
            [
                {"start_time": "2000-01-01", "end_time": "2000-01-08"},
                {"start_time": "2000-01-08", "end_time": "2000-01-15"},
                {"start_time": "2000-01-15", "end_time": "2000-01-22"},
                {"start_time": "2000-01-22", "end_time": "2000-01-29"},
                {"start_time": "2000-01-29", "end_time": "2000-02-05"},
                {"start_time": "2000-02-05", "end_time": "2000-02-10"},
            ],
        ),
        # for Daily streams
        (
            31,
            [
                {"start_time": "2000-01-01", "end_time": "2000-02-01"},
                {"start_time": "2000-02-01", "end_time": "2000-02-10"},
            ],
        ),
        # when start-end period == slice period
        (
            40,
            [
                {"start_time": "2000-01-01", "end_time": "2000-02-10"},
            ],
        ),
        # when start-end period > slice period
        (
            100,
            [
                {"start_time": "2000-01-01", "end_time": "2000-02-10"},
            ],
        ),
    ],
)
def test_date_slices(slice_period, expected_date_slices):
    stats_stream.slice_period = slice_period
    date_slices = stats_stream.date_slices()
    assert date_slices == expected_date_slices


response_organizations = {
    "organizations": [
        {
            "organization": {
                "id": "organization_id_1",
                "updated_at": "2020-12-15T22:35:17.819Z",
                "created_at": "2020-12-15T11:13:03.910Z",
            }
        }
    ]
}


def test_organizations(requests_mock):

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    stream = Organizations(**config_mock)
    records = stream.read_records(sync_mode=SyncMode.full_refresh)
    assert list(records) == [
        {
            "id": "organization_id_1",
            "updated_at": "2020-12-15T22:35:17.819Z",
            "created_at": "2020-12-15T11:13:03.910Z",
        }
    ]


response_adaccounts = {
    "adaccounts": [
        {
            "adaccount": {
                "id": "adaccount_id_1",
                "updated_at": "2020-12-15T22:35:17.819Z",
                "created_at": "2020-12-15T11:13:03.910Z",
            }
        },
        {
            "adaccount": {
                "id": "adaccount_id_2",
                "updated_at": "2020-12-15T22:35:17.819Z",
                "created_at": "2020-12-15T11:13:03.910Z",
            }
        },
    ]
}


def run_stream(stream):
    slices = stream.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        yield from stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)


def test_accounts(requests_mock):

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)

    stream = Adaccounts(**config_mock)
    records = run_stream(stream)
    assert list(records) == [
        {
            "id": "adaccount_id_1",
            "updated_at": "2020-12-15T22:35:17.819Z",
            "created_at": "2020-12-15T11:13:03.910Z",
        },
        {
            "id": "adaccount_id_2",
            "updated_at": "2020-12-15T22:35:17.819Z",
            "created_at": "2020-12-15T11:13:03.910Z",
        },
    ]


response_ads = {
    "ads": [
        {
            "ad": {
                "id": "ad_id_1",
                "updated_at": "2020-12-15T22:35:17.819Z",
                "created_at": "2020-12-15T11:13:03.910Z",
            }
        },
        {
            "ad": {
                "id": "ad_id_2",
                "updated_at": "2020-12-15T22:35:17.819Z",
                "created_at": "2020-12-15T11:13:03.910Z",
            }
        },
    ]
}


def test_ads(requests_mock):

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)

    stream = Ads(**config_mock)
    records = run_stream(stream)
    assert list(records) == [
        {
            "id": "ad_id_1",
            "updated_at": "2020-12-15T22:35:17.819Z",
            "created_at": "2020-12-15T11:13:03.910Z",
        },
        {
            "id": "ad_id_2",
            "updated_at": "2020-12-15T22:35:17.819Z",
            "created_at": "2020-12-15T11:13:03.910Z",
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

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_1/stats", json=response_ads_stats_lifetime_1)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_2/stats", json=response_ads_stats_lifetime_2)

    stream = AdsStatsLifetime(**config_mock)
    records = run_stream(stream)
    assert list(records) == [
        {
            "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            "end_time": "2022-07-01T07:00:00.000-07:00",
            "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
            "granularity": "LIFETIME",
            "id": "ad_id_1",
            "impressions": 0,
            "start_time": "2016-09-26T00:00:00.000-07:00",
            "swipes": 0,
            "type": "AD",
        },
        {
            "conversion_data_processed_end_time": "2022-07-01T00:00:00.000Z",
            "end_time": "2022-07-01T07:00:00.000-07:00",
            "finalized_data_end_time": "2022-07-01T07:00:00.000-07:00",
            "granularity": "LIFETIME",
            "id": "ad_id_2",
            "impressions": 0,
            "start_time": "2016-09-26T00:00:00.000-07:00",
            "swipes": 0,
            "type": "AD",
        },
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
                "start_time": "2022-06-25T00:00:00.000-07:00",
                "end_time": "2022-06-29T00:00:00.000-07:00",
                "finalized_data_end_time": "2022-06-30T00:00:00.000-07:00",
                "conversion_data_processed_end_time": "2022-06-30T00:00:00.000Z",
                "timeseries": [
                    {
                        "start_time": "2022-06-25T00:00:00.000-07:00",
                        "end_time": "2022-06-26T00:00:00.000-07:00",
                        "stats": {
                            "impressions": 0,
                            "swipes": 0,
                            "quartile_1": 0,
                            "quartile_2": 0,
                            "quartile_3": 0,
                        },
                    },
                    {
                        "start_time": "2022-06-26T00:00:00.000-07:00",
                        "end_time": "2022-06-27T00:00:00.000-07:00",
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

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_1/ads", json={"ads": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/adaccounts/adaccount_id_2/ads", json=response_ads)
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_1/stats", json={"timeseries_stats": []})
    requests_mock.get("https://adsapi.snapchat.com/v1/ads/ad_id_2/stats", json=response_ads_stats_daily_1)

    stream = AdsStatsDaily(**config_mock)
    records = run_stream(stream)
    assert len(list(records)) == 4  # 2 records for each of 2 slices


def test_get_parent_ids(requests_mock):
    """Test cache usage in get_parent_ids"""
    # nonlocal auxiliary_id_map

    requests_mock.get("https://adsapi.snapchat.com/v1/me/organizations", json=response_organizations)
    requests_mock.get("https://adsapi.snapchat.com/v1/organizations/organization_id_1/adaccounts", json=response_adaccounts)

    stream = Adaccounts(**config_mock)

    # reset cache, it can be filled by calls in previous tests
    source_snapchat_marketing.source.auxiliary_id_map = {}

    # 1st call
    list(run_stream(stream))
    # 1st request to organizations
    # 2nd request to adaccounts
    assert len(requests_mock.request_history) == 2

    # 2nd call
    list(run_stream(stream))
    # request to organizations is skipped due to cache
    # 3rd request to adaccounts
    assert len(requests_mock.request_history) == 3


def test_source_streams():
    source_config = {"client_id": "XXX", "client_secret": "XXX", "refresh_token": "XXX", "start_date": "2022-05-25"}
    streams = SourceSnapchatMarketing().streams(config=source_config)
    assert len(streams) == 20


def test_source_check_connection(requests_mock):
    source_config = {"client_id": "XXX", "client_secret": "XXX", "refresh_token": "XXX", "start_date": "2022-05-25"}
    requests_mock.post("https://accounts.snapchat.com/login/oauth2/access_token", json={"access_token": "XXX", "expires_in": 3600})
    requests_mock.get("https://adsapi.snapchat.com/v1/me", json={})

    results = SourceSnapchatMarketing().check_connection(logger=None, config=source_config)
    assert results == (True, None)


def test_retry_get_access_token(requests_mock):
    requests_mock.register_uri(
        "POST",
        "https://accounts.snapchat.com/login/oauth2/access_token",
        [{"status_code": 429}, {"status_code": 429}, {"status_code": 200, "json": {"access_token": "token", "expires_in": 3600}}],
    )
    auth = SnapchatOauth2Authenticator(
        token_refresh_endpoint="https://accounts.snapchat.com/login/oauth2/access_token",
        client_id="client_id",
        client_secret="client_secret",
        refresh_token="refresh_token",
    )
    token = auth.get_access_token()
    assert len(requests_mock.request_history) == 3
    assert token == "token"


def test_should_retry_403_error(requests_mock):
    requests_mock.register_uri("GET", "https://adsapi.snapchat.com/v1/me/organizations",
                               [{"status_code": 403, "json": {"organizations": []}}])
    stream = Organizations(**config_mock)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

    assert not records
