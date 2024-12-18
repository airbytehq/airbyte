# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from advetiser_slices import mock_advertisers_slices
from config_builder import ConfigBuilder
from source_tiktok_marketing import SourceTiktokMarketing

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder


EMPTY_LIST_RESPONSE = {"code": 0, "message": "ok", "data": {"list": []}}


class TestAdsReportHourly(TestCase):
    stream_name = "ads_reports_hourly"
    advertiser_id = "872746382648"
    cursor = "2024-01-01 10:00:00"
    cursor_field = "stat_time_hour"
    metrics = [
        "campaign_name",
        "campaign_id",
        "adgroup_name",
        "placement_type",
        "tt_app_id",
        "tt_app_name",
        "mobile_app_id",
        "promotion_type",
        "dpa_target_audience_type",
        "conversion",
        "cost_per_conversion",
        "conversion_rate",
        "real_time_conversion",
        "real_time_cost_per_conversion",
        "real_time_conversion_rate",
        "result",
        "cost_per_result",
        "result_rate",
        "real_time_result",
        "real_time_cost_per_result",
        "real_time_result_rate",
        "secondary_goal_result",
        "cost_per_secondary_goal_result",
        "secondary_goal_result_rate",
        "adgroup_id",
        "ad_name",
        "ad_text",
        "total_purchase_value",
        "total_onsite_shopping_value",
        "onsite_shopping",
        "vta_purchase",
        "vta_conversion",
        "cta_purchase",
        "cta_conversion",
        "total_pageview",
        "complete_payment",
        "value_per_complete_payment",
        "total_complete_payment_rate",
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

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self, include_deleted: bool = False):
        config_to_build = ConfigBuilder().with_end_date("2024-01-02")
        if include_deleted:
            config_to_build = config_to_build.with_include_deleted()
        return config_to_build.build()

    def state(self):
        return (
            StateBuilder()
            .with_stream_state(
                stream_name=self.stream_name,
                state={
                    "states": [
                        {"partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}, "cursor": {self.cursor_field: self.cursor}}
                    ]
                },
            )
            .build()
        )

    def mock_response(self, http_mocker: HttpMocker, include_deleted=False):
        query_params = {
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_AD",
            "dimensions": '["ad_id", "stat_time_hour"]',
            "metrics": str(self.metrics).replace("'", '"'),
            "start_date": self.config()["start_date"],
            "end_date": self.config()["start_date"],
            "page_size": 1000,
            "advertiser_id": self.advertiser_id,
        }
        if include_deleted:
            query_params["filtering"] = '[{"field_name": "ad_status", "filter_type": "IN", "filter_value": "[\\"STATUS_ALL\\"]"}]'
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )
        query_params["start_date"] = query_params["end_date"] = self.config()["end_date"]

        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

    @HttpMocker()
    def test_basic_read(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(SourceTiktokMarketing(), self.config(), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("ad_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None

    @HttpMocker()
    def test_read_with_state(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(
            source=SourceTiktokMarketing(), config=self.config(), catalog=self.catalog(sync_mode=SyncMode.incremental), state=self.state()
        )

        assert len(output.records) == 1
        assert output.state_messages[0].state.stream.stream_state.states == [
            {"cursor": {"stat_time_hour": self.cursor}, "partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}}
        ]

    @HttpMocker()
    def test_read_with_include_deleted(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker, include_deleted=True)

        output = read(SourceTiktokMarketing(), self.config(include_deleted=True), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("ad_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None


class TestAdGroupsReportsHourly(TestCase):
    stream_name = "ad_groups_reports_hourly"
    advertiser_id = "872746382648"
    cursor = "2024-01-01 10:00:00"
    cursor_field = "stat_time_hour"
    metrics = [
        "campaign_name",
        "campaign_id",
        "adgroup_name",
        "placement_type",
        "tt_app_id",
        "tt_app_name",
        "mobile_app_id",
        "promotion_type",
        "dpa_target_audience_type",
        "conversion",
        "cost_per_conversion",
        "conversion_rate",
        "real_time_conversion",
        "real_time_cost_per_conversion",
        "real_time_conversion_rate",
        "result",
        "cost_per_result",
        "result_rate",
        "real_time_result",
        "real_time_cost_per_result",
        "real_time_result_rate",
        "secondary_goal_result",
        "cost_per_secondary_goal_result",
        "secondary_goal_result_rate",
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

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self, include_deleted: bool = False):
        config_to_build = ConfigBuilder().with_end_date("2024-01-02")
        if include_deleted:
            config_to_build = config_to_build.with_include_deleted()
        return config_to_build.build()

    def state(self):
        return (
            StateBuilder()
            .with_stream_state(
                stream_name=self.stream_name,
                state={
                    "states": [
                        {"partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}, "cursor": {self.cursor_field: self.cursor}}
                    ]
                },
            )
            .build()
        )

    @HttpMocker()
    def test_basic_read(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        query_params = {
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_ADGROUP",
            "dimensions": '["adgroup_id", "stat_time_hour"]',
            "metrics": str(self.metrics).replace("'", '"'),
            "start_date": self.config()["start_date"],
            "end_date": self.config()["start_date"],
            "page_size": 1000,
            "advertiser_id": self.advertiser_id,
        }
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )
        query_params["start_date"] = query_params["end_date"] = self.config()["end_date"]
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

        output = read(SourceTiktokMarketing(), self.config(), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("adgroup_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None

    @HttpMocker()
    def test_read_with_state(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())

        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params={
                    "service_type": "AUCTION",
                    "report_type": "BASIC",
                    "data_level": "AUCTION_ADGROUP",
                    "dimensions": '["adgroup_id", "stat_time_hour"]',
                    "metrics": str(self.metrics).replace("'", '"'),
                    "start_date": self.config()["start_date"],
                    "end_date": self.config()["start_date"],
                    "page_size": 1000,
                    "advertiser_id": self.advertiser_id,
                },
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )

        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params={
                    "service_type": "AUCTION",
                    "report_type": "BASIC",
                    "data_level": "AUCTION_ADGROUP",
                    "dimensions": '["adgroup_id", "stat_time_hour"]',
                    "metrics": str(self.metrics).replace("'", '"'),
                    "start_date": self.config()["end_date"],
                    "end_date": self.config()["end_date"],
                    "page_size": 1000,
                    "advertiser_id": self.advertiser_id,
                },
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

        output = read(
            source=SourceTiktokMarketing(), config=self.config(), catalog=self.catalog(sync_mode=SyncMode.incremental), state=self.state()
        )

        assert len(output.records) == 1
        assert output.state_messages[0].state.stream.stream_state.states == [
            {"cursor": {"stat_time_hour": self.cursor}, "partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}}
        ]

    @HttpMocker()
    def test_read_with_include_deleted(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        filtering = '[{"field_name": "adgroup_status", "filter_type": "IN", "filter_value": "[\\"STATUS_ALL\\"]"}]'
        query_params = {
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_ADGROUP",
            "dimensions": '["adgroup_id", "stat_time_hour"]',
            "metrics": str(self.metrics).replace("'", '"'),
            "start_date": self.config()["start_date"],
            "end_date": self.config()["start_date"],
            "page_size": 1000,
            "advertiser_id": self.advertiser_id,
            "filtering": filtering,
        }
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )
        query_params["start_date"] = query_params["end_date"] = self.config()["end_date"]
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

        output = read(SourceTiktokMarketing(), self.config(include_deleted=True), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("adgroup_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None


class TestAdvertisersReportsHourly(TestCase):
    stream_name = "advertisers_reports_hourly"
    advertiser_id = "872746382648"
    cursor = "2024-01-01 10:00:00"
    cursor_field = "stat_time_hour"
    metrics = [
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

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().with_end_date("2024-01-02").build()

    def state(self):
        return (
            StateBuilder()
            .with_stream_state(
                stream_name=self.stream_name,
                state={
                    "states": [
                        {"partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}, "cursor": {self.cursor_field: self.cursor}}
                    ]
                },
            )
            .build()
        )

    def mock_response(self, http_mocker: HttpMocker):
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params={
                    "service_type": "AUCTION",
                    "report_type": "BASIC",
                    "data_level": "AUCTION_ADVERTISER",
                    "dimensions": '["advertiser_id", "stat_time_hour"]',
                    "metrics": str(self.metrics).replace("'", '"'),
                    "start_date": self.config()["start_date"],
                    "end_date": self.config()["start_date"],
                    "page_size": 1000,
                    "advertiser_id": self.advertiser_id,
                },
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )

        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params={
                    "service_type": "AUCTION",
                    "report_type": "BASIC",
                    "data_level": "AUCTION_ADVERTISER",
                    "dimensions": '["advertiser_id", "stat_time_hour"]',
                    "metrics": str(self.metrics).replace("'", '"'),
                    "start_date": self.config()["end_date"],
                    "end_date": self.config()["end_date"],
                    "page_size": 1000,
                    "advertiser_id": self.advertiser_id,
                },
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

    @HttpMocker()
    def test_basic_read(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(SourceTiktokMarketing(), self.config(), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("advertiser_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None

    @HttpMocker()
    def test_read_with_state(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(
            source=SourceTiktokMarketing(), config=self.config(), catalog=self.catalog(sync_mode=SyncMode.incremental), state=self.state()
        )

        assert len(output.records) == 1
        assert output.state_messages[0].state.stream.stream_state.states == [
            {"cursor": {"stat_time_hour": self.cursor}, "partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}}
        ]


class TestCampaignsReportsHourly(TestCase):
    stream_name = "campaigns_reports_hourly"
    advertiser_id = "872746382648"
    cursor = "2024-01-01 10:00:00"
    cursor_field = "stat_time_hour"
    metrics = [
        "campaign_name",
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

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self, include_deleted: bool = False):
        config_to_build = ConfigBuilder().with_end_date("2024-01-02")
        if include_deleted:
            config_to_build = config_to_build.with_include_deleted()
        return config_to_build.build()

    def state(self):
        return (
            StateBuilder()
            .with_stream_state(
                stream_name=self.stream_name,
                state={
                    "states": [
                        {"partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}, "cursor": {self.cursor_field: self.cursor}}
                    ]
                },
            )
            .build()
        )

    def mock_response(self, http_mocker: HttpMocker, include_deleted: bool = False):
        query_params = {
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_CAMPAIGN",
            "dimensions": '["campaign_id", "stat_time_hour"]',
            "metrics": str(self.metrics).replace("'", '"'),
            "start_date": self.config()["start_date"],
            "end_date": self.config()["start_date"],
            "page_size": 1000,
            "advertiser_id": self.advertiser_id,
        }
        if include_deleted:
            query_params["filtering"] = '[{"field_name": "campaign_status", "filter_type": "IN", "filter_value": "[\\"STATUS_ALL\\"]"}]'
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )

        query_params["start_date"] = query_params["end_date"] = self.config()["end_date"]
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(EMPTY_LIST_RESPONSE), status_code=200),
        )

    @HttpMocker()
    def test_basic_read(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(SourceTiktokMarketing(), self.config(), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("campaign_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None

    @HttpMocker()
    def test_read_with_state(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker)

        output = read(
            source=SourceTiktokMarketing(), config=self.config(), catalog=self.catalog(sync_mode=SyncMode.incremental), state=self.state()
        )

        assert len(output.records) == 1
        assert output.state_messages[0].state.stream.stream_state.states == [
            {"cursor": {"stat_time_hour": self.cursor}, "partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}}}
        ]

    @HttpMocker()
    def test_read_with_include_deleted(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, self.config())
        self.mock_response(http_mocker, include_deleted=True)

        output = read(SourceTiktokMarketing(), self.config(include_deleted=True), self.catalog())
        assert len(output.records) == 2
        assert output.records[0].record.data.get("campaign_id") is not None
        assert output.records[0].record.data.get("stat_time_hour") is not None
