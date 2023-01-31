#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, PropertyMock, patch

import pendulum
import pytest
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


def test_stream_slices_advertisers():
    slices = Advertisers(**CONFIG).stream_slices()
    assert list(slices) == [None]


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
            ReportGranularity.LIFETIME,
            [
                {"advertiser_id": 1, "end_date": END_DATE, "start_date": START_DATE},
                {"advertiser_id": 2, "end_date": END_DATE, "start_date": START_DATE},
            ],
        ),
        (
            ReportGranularity.DAY,
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
    config = {**{"report_granularity": granularity}, **CONFIG}
    slices = AdsReports(**config).stream_slices()
    assert list(slices) == slices_expected


@pytest.mark.parametrize(
    "stream, metrics_number",
    [
        (AdsReports, 36),
        (AdGroupsReports, 33),
        (AdvertisersReports, 11),
        (CampaignsReports, 10),
        (AdvertisersAudienceReports, 6),
        (AdsAudienceReports, 30),
    ],
)
def test_basic_reports_get_metrics_day(stream, metrics_number):
    config = {**{"report_granularity": ReportGranularity.DAY}, **CONFIG}
    metrics = stream(**config)._get_metrics()
    assert len(metrics) == metrics_number


@pytest.mark.parametrize(
    "stream, metrics_number",
    [
        (AdsReports, 36),
        (AdGroupsReports, 33),
        (AdvertisersReports, 9),
        (CampaignsReports, 10),
        (AdvertisersAudienceReports, 6),
    ],
)
def test_basic_reports_get_metrics_lifetime(stream, metrics_number):
    config = {**{"report_granularity": ReportGranularity.LIFETIME}, **CONFIG}
    metrics = stream(**config)._get_metrics()
    assert len(metrics) == metrics_number


@pytest.mark.parametrize(
    "stream, dimensions_expected",
    [
        (AdsReports, ["ad_id"]),
        (AdGroupsReports, ["adgroup_id"]),
        (AdvertisersReports, ["advertiser_id"]),
        (CampaignsReports, ["campaign_id"]),
        (AdvertisersAudienceReports, ["advertiser_id"]),
    ],
)
def test_basic_reports_get_reporting_dimensions_lifetime(stream, dimensions_expected):
    config = {**{"report_granularity": ReportGranularity.LIFETIME}, **CONFIG}
    dimensions = stream(**config)._get_reporting_dimensions()
    assert dimensions == dimensions_expected


@pytest.mark.parametrize(
    "stream, dimensions_expected",
    [
        (AdsReports, ["ad_id", "stat_time_day"]),
        (AdGroupsReports, ["adgroup_id", "stat_time_day"]),
        (AdvertisersReports, ["advertiser_id", "stat_time_day"]),
        (CampaignsReports, ["campaign_id", "stat_time_day"]),
        (AdvertisersAudienceReports, ["advertiser_id", "stat_time_day"]),
    ],
)
def test_basic_reports_get_reporting_dimensions_day(stream, dimensions_expected):
    config = {**{"report_granularity": ReportGranularity.DAY}, **CONFIG}
    dimensions = stream(**config)._get_reporting_dimensions()
    assert dimensions == dimensions_expected


@pytest.mark.parametrize(
    "granularity, cursor_field_expected",
    [
        (ReportGranularity.DAY, ["dimensions", "stat_time_day"]),
        (ReportGranularity.HOUR, ["dimensions", "stat_time_hour"]),
        (ReportGranularity.LIFETIME, []),
    ],
)
def test_basic_reports_cursor_field(granularity, cursor_field_expected):
    config = {**{"report_granularity": granularity}, **CONFIG}
    ads_reports = AdvertisersReports(**config)
    cursor_field = ads_reports.cursor_field
    assert cursor_field == cursor_field_expected


def test_request_params():
    stream_slice = {"advertiser_id": 1, "start_date": "2020", "end_date": "2021"}
    config = {**{"report_granularity": ReportGranularity.DAY}, **CONFIG}
    params = AdvertisersAudienceReports(**config).request_params(stream_slice=stream_slice)
    assert params == {
        "advertiser_id": 1,
        "data_level": "AUCTION_ADVERTISER",
        "dimensions": '["advertiser_id", "stat_time_day", "gender", "age"]',
        "end_date": "2021",
        "metrics": '["spend", "cpc", "cpm", "impressions", "clicks", "ctr"]',
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
        state2_modify_time = state2["modify_time"]  # state2_modify_time is JsonUpdatedState object
        assert state2_modify_time.dict() == "2020-01-08 00:00:00"
