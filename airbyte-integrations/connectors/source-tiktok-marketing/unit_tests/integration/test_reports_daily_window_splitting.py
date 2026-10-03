# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source
from .advetiser_slices import mock_advertisers_slices
from .config_builder import ConfigBuilder


_REPORT_URL = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
_ADVERTISER_ID = "872746382648"
_QUERY_TOO_LARGE = {"code": 40067, "message": "The query is too large, please narrow the date range", "data": {}}
_METRICS = [
    "cash_spend",
    "voucher_spend",
    "spend",
    "cpc",
    "cpm",
    "impressions",
    "clicks",
    "ctr",
    "reach",
    "cost_per_1000_reached",
    "frequency",
    "video_play_actions",
    "video_watched_2s",
    "video_watched_6s",
    "average_video_play",
    "average_video_play_per_user",
    "video_views_p25",
    "video_views_p50",
    "video_views_p75",
    "video_views_p100",
    "profile_visits",
    "likes",
    "comments",
    "shares",
    "follows",
    "clicks_on_music_disc",
    "real_time_app_install",
    "real_time_app_install_cost",
    "app_install",
]


def _report_request(start_date: str, end_date: str) -> HttpRequest:
    return HttpRequest(
        url=_REPORT_URL,
        query_params={
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_ADVERTISER",
            "dimensions": '["advertiser_id", "stat_time_day"]',
            "metrics": json.dumps(_METRICS),
            "start_date": start_date,
            "end_date": end_date,
            "page_size": 1000,
            "advertiser_id": _ADVERTISER_ID,
        },
    )


def _report_response(*days: str) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [
                        {"dimensions": {"advertiser_id": _ADVERTISER_ID, "stat_time_day": f"{day} 00:00:00"}, "metrics": {"spend": "1.00"}}
                        for day in days
                    ],
                    "page_info": {"total_number": len(days), "page": 1, "page_size": 1000, "total_page": 1},
                },
            }
        ),
        status_code=200,
    )


@freeze_time("2024-10-15")
class TestAdvertisersReportsDailyWindowSplitting(TestCase):
    """
    The daily report streams read one `report_granularity`-day window per advertiser. When TikTok rejects a
    window with error 40067 ("query too large"), the CDK halves that advertiser's window and reads each half.
    """

    stream_name = "advertisers_reports_daily"

    def config(self) -> dict:
        config = ConfigBuilder().with_end_date("2024-09-30").build()
        config["start_date"] = "2024-09-01"
        config["report_granularity"] = 30
        return config

    def catalog(self):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=SyncMode.incremental).build()

    def _read(self, expecting_exception: bool = False):
        config = self.config()
        return read(get_source(config=config, state=None), config, self.catalog(), expecting_exception=expecting_exception)

    @HttpMocker()
    def test_given_40067_when_read_then_split_window_in_halves(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        http_mocker.get(_report_request("2024-09-01", "2024-09-30"), HttpResponse(body=json.dumps(_QUERY_TOO_LARGE), status_code=200))
        http_mocker.get(_report_request("2024-09-01", "2024-09-15"), _report_response("2024-09-03"))
        http_mocker.get(_report_request("2024-09-16", "2024-09-30"), _report_response("2024-09-20"))

        output = self._read()

        assert not output.errors
        assert sorted(record.record.data["stat_time_day"] for record in output.records) == ["2024-09-03 00:00:00", "2024-09-20 00:00:00"]
        state = output.most_recent_state.stream_state.__dict__
        assert state["states"] == [
            {"partition": {"advertiser_id": _ADVERTISER_ID, "parent_slice": {}}, "cursor": {"stat_time_day": "2024-09-20"}}
        ]

    @HttpMocker()
    def test_given_half_also_too_large_when_read_then_split_again(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        http_mocker.get(_report_request("2024-09-01", "2024-09-30"), HttpResponse(body=json.dumps(_QUERY_TOO_LARGE), status_code=200))
        http_mocker.get(_report_request("2024-09-01", "2024-09-15"), _report_response("2024-09-03"))
        http_mocker.get(_report_request("2024-09-16", "2024-09-30"), HttpResponse(body=json.dumps(_QUERY_TOO_LARGE), status_code=200))
        http_mocker.get(_report_request("2024-09-16", "2024-09-22"), _report_response("2024-09-20"))
        http_mocker.get(_report_request("2024-09-23", "2024-09-30"), _report_response("2024-09-25"))

        output = self._read()

        assert not output.errors
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_single_day_still_too_large_when_read_then_transient_error(self, http_mocker: HttpMocker):
        """
        A 2-day window is rejected, then its 1-day half is rejected too, so the connector can't narrow it
        further. The sync fails as a transient_error (the platform retries it) instead of the config_error the
        connector used to raise. (A config with start_date == end_date produces no window at all.)
        """
        config = self.config()
        config["end_date"] = "2024-09-02"
        mock_advertisers_slices(http_mocker, config)
        http_mocker.get(_report_request("2024-09-01", "2024-09-02"), HttpResponse(body=json.dumps(_QUERY_TOO_LARGE), status_code=200))
        http_mocker.get(_report_request("2024-09-01", "2024-09-01"), HttpResponse(body=json.dumps(_QUERY_TOO_LARGE), status_code=200))

        output = read(get_source(config=config, state=None), config, self.catalog(), expecting_exception=True)

        assert not output.records
        assert output.errors[0].trace.error.failure_type == FailureType.transient_error
        assert "rejected a daily report request for a single day" in output.errors[0].trace.error.message
