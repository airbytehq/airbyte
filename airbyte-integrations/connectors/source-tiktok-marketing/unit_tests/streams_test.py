#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch

import pendulum
import pytest
import requests
from source_tiktok_marketing.source import get_report_stream
from source_tiktok_marketing.streams import (
    AdGroupsReports,
    Ads,
    AdsAudienceReports,
    AdsReports,
    Advertisers,
    AdvertisersAudienceReports,
    AdvertisersReports,
    BasicReports,
    CampaignsReports,
    Daily,
    FullRefreshTiktokStream,
    Hourly,
    Lifetime,
    ReportGranularity,
)

START_DATE = "2020-01-01"
END_DATE = "2020-03-01"
CONFIG = {
    "access_token": "access_token",
    "secret": "secret",
    "authenticator": None,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "app_id": 1234,
    "advertiser_id": 0,
    "include_deleted": True,
}
CONFIG_SANDBOX = {
    "access_token": "access_token",
    "secret": "secret",
    "authenticator": None,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "app_id": 1234,
    "advertiser_id": 2000,
}
ADV_IDS = [{"advertiser_id": 1}, {"advertiser_id": 2}]


@pytest.fixture(scope="module")
def pendulum_now_mock():
    with patch.object(pendulum, "now", return_value=pendulum.parse(END_DATE)):
        yield


@pytest.fixture(name="advertiser_ids")
def advertiser_ids_fixture():
    with patch("source_tiktok_marketing.streams.AdvertiserIds") as advertiser_ids_stream:
        advertiser_ids_stream().read_records = MagicMock(return_value=ADV_IDS)
        yield


@pytest.mark.parametrize(
    "granularity,intervals_len",
    [
        (ReportGranularity.LIFETIME, 1),
        (ReportGranularity.DAY, 3),
        (ReportGranularity.HOUR, 61),
    ],
)
def test_get_time_interval(pendulum_now_mock, granularity, intervals_len):
    intervals = BasicReports._get_time_interval(start_date="2020-01-01", ending_date="2020-03-01", granularity=granularity)
    assert len(list(intervals)) == intervals_len


@patch.object(pendulum, "now", return_value=pendulum.parse("2018-12-25"))
def test_get_time_interval_past(pendulum_now_mock_past):
    intervals = BasicReports._get_time_interval(start_date="2020-01-01", ending_date="2020-01-01", granularity=ReportGranularity.DAY)
    assert len(list(intervals)) == 1


@patch("source_tiktok_marketing.streams.AdvertiserIds.read_records", MagicMock(return_value=[{"advertiser_id": i} for i in range(354)]))
def test_stream_slices_advertisers():
    slices = Advertisers(**CONFIG).stream_slices()
    assert len(list(slices)) == 4  # math.ceil(354 / 100)


@pytest.mark.parametrize(
    "config_name, slices_expected",
    [
        (CONFIG, ADV_IDS),
        (CONFIG_SANDBOX, [{"advertiser_id": 2000}]),
    ],
)
def test_stream_slices_basic_sandbox(advertiser_ids, config_name, slices_expected):
    slices = Ads(**config_name).stream_slices()
    assert list(slices) == slices_expected


@pytest.mark.parametrize(
    "granularity, slices_expected",
    [
        (
            Lifetime,
            [
                {"advertiser_id": 1, "end_date": END_DATE, "start_date": START_DATE},
                {"advertiser_id": 2, "end_date": END_DATE, "start_date": START_DATE},
            ],
        ),
        (
            Daily,
            [
                {"advertiser_id": 1, "end_date": "2020-01-30", "start_date": "2020-01-01"},
                {"advertiser_id": 1, "end_date": "2020-02-29", "start_date": "2020-01-31"},
                {"advertiser_id": 1, "end_date": "2020-03-01", "start_date": "2020-03-01"},
                {"advertiser_id": 2, "end_date": "2020-01-30", "start_date": "2020-01-01"},
                {"advertiser_id": 2, "end_date": "2020-02-29", "start_date": "2020-01-31"},
                {"advertiser_id": 2, "end_date": "2020-03-01", "start_date": "2020-03-01"},
            ],
        ),
    ],
)
def test_stream_slices_report(advertiser_ids, granularity, slices_expected, pendulum_now_mock):
    slices = get_report_stream(AdsReports, granularity)(**CONFIG).stream_slices()
    assert list(slices) == slices_expected


@pytest.mark.parametrize(
    "stream, metrics_number",
    [
        (AdsReports, 65),
        (AdGroupsReports, 51),
        (AdvertisersReports, 29),
        (CampaignsReports, 28),
        (AdvertisersAudienceReports, 6),
        (AdsAudienceReports, 30),
    ],
)
def test_basic_reports_get_metrics_day(stream, metrics_number):
    metrics = get_report_stream(stream, Daily)(**CONFIG)._get_metrics()
    assert len(metrics) == metrics_number


@pytest.mark.parametrize(
    "stream, metrics_number",
    [
        (AdsReports, 65),
        (AdGroupsReports, 51),
        (AdvertisersReports, 27),
        (CampaignsReports, 28),
        (AdvertisersAudienceReports, 6),
    ],
)
def test_basic_reports_get_metrics_lifetime(stream, metrics_number):
    metrics = get_report_stream(stream, Lifetime)(**CONFIG)._get_metrics()
    assert len(metrics) == metrics_number


@pytest.mark.parametrize(
    "stream, dimensions_expected",
    [
        (AdsReports, ["ad_id"]),
        (AdGroupsReports, ["adgroup_id"]),
        (AdvertisersReports, ["advertiser_id"]),
        (CampaignsReports, ["campaign_id"]),
        (AdvertisersAudienceReports, ["advertiser_id", "gender", "age"]),
    ],
)
def test_basic_reports_get_reporting_dimensions_lifetime(stream, dimensions_expected):
    dimensions = get_report_stream(stream, Lifetime)(**CONFIG)._get_reporting_dimensions()
    assert dimensions == dimensions_expected


@pytest.mark.parametrize(
    "stream, dimensions_expected",
    [
        (AdsReports, ["ad_id", "stat_time_day"]),
        (AdGroupsReports, ["adgroup_id", "stat_time_day"]),
        (AdvertisersReports, ["advertiser_id", "stat_time_day"]),
        (CampaignsReports, ["campaign_id", "stat_time_day"]),
        (AdvertisersAudienceReports, ["advertiser_id", "stat_time_day", "gender", "age"]),
    ],
)
def test_basic_reports_get_reporting_dimensions_day(stream, dimensions_expected):
    dimensions = get_report_stream(stream, Daily)(**CONFIG)._get_reporting_dimensions()
    assert dimensions == dimensions_expected


@pytest.mark.parametrize(
    "granularity, cursor_field_expected",
    [
        (Daily, "stat_time_day"),
        (Hourly, "stat_time_hour"),
        (Lifetime, []),
    ],
)
def test_basic_reports_cursor_field(granularity, cursor_field_expected):
    ads_reports = get_report_stream(AdsReports, granularity)(**CONFIG)
    cursor_field = ads_reports.cursor_field
    assert cursor_field == cursor_field_expected


@pytest.mark.parametrize(
    "granularity, cursor_field_expected",
    [
        (Daily, ["dimensions", "stat_time_day"]),
        (Hourly, ["dimensions", "stat_time_hour"]),
        (Lifetime, ["dimensions", "stat_time_day"]),
    ],
)
def test_basic_reports_deprecated_cursor_field(granularity, cursor_field_expected):
    ads_reports = get_report_stream(AdsReports, granularity)(**CONFIG)
    deprecated_cursor_field = ads_reports.deprecated_cursor_field
    assert deprecated_cursor_field == cursor_field_expected


def test_request_params():
    stream_slice = {"advertiser_id": 1, "start_date": "2020", "end_date": "2021"}
    params = get_report_stream(AdvertisersAudienceReports, Daily)(**CONFIG).request_params(stream_slice=stream_slice)
    assert params == {
        "advertiser_id": 1,
        "data_level": "AUCTION_ADVERTISER",
        "dimensions": '["advertiser_id", "stat_time_day", "gender", "age"]',
        "end_date": "2021",
        "metrics": '["spend", "cpc", "cpm", "impressions", "clicks", "ctr"]',
        "filters": '[{"filter_value": ["STATUS_ALL"], "field_name": "ad_status", "filter_type": "IN"}, {"filter_value": ["STATUS_ALL"], "field_name": "campaign_status", "filter_type": "IN"}, {"filter_value": ["STATUS_ALL"], "field_name": "adgroup_status", "filter_type": "IN"}]',
        "page_size": 1000,
        "report_type": "AUDIENCE",
        "service_type": "AUCTION",
        "start_date": "2020",
    }


def test_get_updated_state():
    with patch.object(Ads, "is_finished", new_callable=PropertyMock) as is_finished:

        ads = Ads(**CONFIG_SANDBOX)

        # initial state.
        state = {}

        # state should be empty while stream is reading records
        ads.max_cursor_date = "2020-01-08 00:00:00"
        is_finished.return_value = False
        state1 = ads.get_updated_state(current_stream_state=state, latest_record={})
        assert state1 == {"modify_time": ""}

        # state should be updated only when all records have been read (is_finished = True)
        is_finished.return_value = True
        state2 = ads.get_updated_state(current_stream_state=state, latest_record={})
        # state2_modify_time is JsonUpdatedState object
        state2_modify_time = state2["modify_time"]
        assert state2_modify_time.dict() == "2020-01-08 00:00:00"


def test_get_updated_state_no_cursor_field():
    """
    Some full_refresh streams (which don't define a cursor) inherit the get_updated_state() method from an incremental
    stream. This test verifies that the stream does not attempt to extract the cursor value from the latest record
    """
    ads_reports = AdsReports(**CONFIG_SANDBOX)
    state1 = ads_reports.get_updated_state(current_stream_state={}, latest_record={})
    assert state1 == {}


@pytest.mark.parametrize(
    "value, expected",
    [
        (["str1", "str2", "str3"], '["str1", "str2", "str3"]'),
        ([1, 2, 3], "[1, 2, 3]"),
    ],
)
def test_convert_array_param(value, expected):
    stream = Advertisers("2021-01-01", "2021-01-02")
    test = stream.convert_array_param(value)
    assert test == expected


def test_no_next_page_token(requests_mock):
    stream = Advertisers("2021-01-01", "2021-01-02")
    url = stream.url_base + stream.path()
    requests_mock.get(url, json={"data": {"page_info": {}}})
    test_response = requests.get(url)
    assert stream.next_page_token(test_response) is None


@pytest.mark.parametrize(
    ("original_value", "expected_value"),
    (("-", None), (26.10, Decimal(26.10)), ("some_str", "some_str")),
)
def test_transform_function(original_value, expected_value):
    field_schema = {}
    assert FullRefreshTiktokStream.transform_function(original_value, field_schema) == expected_value
