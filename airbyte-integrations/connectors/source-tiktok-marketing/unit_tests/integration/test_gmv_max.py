# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source
from .advetiser_slices import mock_advertisers_slices
from .config_builder import ConfigBuilder


BASE_URL = "https://business-api.tiktok.com/open_api/v1.3/"
ADVERTISER_ID = "872746382648"
PRODUCT_METRICS = [
    "cost",
    "net_cost",
    "orders",
    "cost_per_order",
    "gross_revenue",
    "roi",
    "product_impressions",
    "product_clicks",
    "product_click_rate",
    "ad_click_rate",
    "ad_conversion_rate",
]
LIVE_METRICS = PRODUCT_METRICS + [
    "live_views",
    "cost_per_live_view",
    "10_second_live_views",
    "cost_per_10_second_live_view",
    "live_follows",
]


def catalog(stream_name: str):
    return CatalogBuilder().with_stream(name=stream_name, sync_mode=SyncMode.full_refresh).build()


def config():
    return ConfigBuilder().with_end_date("2024-01-02").build()


def stores_response(stores):
    return {"code": 0, "message": "ok", "data": {"store_list": stores}}


def report_response(campaign_id: str):
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "list": [
                {
                    "dimensions": {"campaign_id": campaign_id, "stat_time_day": "2024-01-01 00:00:00"},
                    "metrics": {
                        "cost": "12.5",
                        "net_cost": "10.0",
                        "orders": "-",
                        "cost_per_order": "1.25",
                        "gross_revenue": "25.0",
                        "roi": "2.0",
                        "product_impressions": "100",
                        "product_clicks": "10",
                        "product_click_rate": "0.1",
                        "ad_click_rate": "0.2",
                        "ad_conversion_rate": "0.05",
                    },
                }
            ],
            "page_info": {"total_number": 1, "page": 1, "page_size": 1000, "total_page": 1},
        },
    }


def mock_stores(http_mocker: HttpMocker, advertiser_id: str, stores):
    http_mocker.get(
        HttpRequest(
            url=f"{BASE_URL}gmv_max/store/list/",
            query_params={"advertiser_id": advertiser_id},
        ),
        HttpResponse(body=json.dumps(stores_response(stores)), status_code=200),
    )


def mock_report(http_mocker: HttpMocker, advertiser_id: str, store_id: str, metrics, promotion_type: str, campaign_id: str):
    request = HttpRequest(
        url=f"{BASE_URL}gmv_max/report/get/",
        query_params={
            "advertiser_id": advertiser_id,
            "store_ids": json.dumps([store_id]),
            "dimensions": json.dumps(["campaign_id", "stat_time_day"]),
            "metrics": json.dumps(metrics),
            "filtering": json.dumps({"gmv_max_promotion_types": [promotion_type]}),
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "page_size": 1000,
        },
    )
    http_mocker.get(
        request,
        HttpResponse(body=json.dumps(report_response(campaign_id)), status_code=200),
    )
    return request


class TestGmvMaxCampaigns(TestCase):
    @HttpMocker()
    def test_requests_each_promotion_type(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, config())
        for promotion_type, records in [
            (
                "PRODUCT_GMV_MAX",
                [{"campaign_id": "campaign-1", "advertiser_id": ADVERTISER_ID}],
            ),
            ("LIVE_GMV_MAX", []),
        ]:
            http_mocker.get(
                HttpRequest(
                    url=f"{BASE_URL}gmv_max/campaign/get/",
                    query_params={
                        "page_size": 100,
                        "advertiser_id": ADVERTISER_ID,
                        "filtering": json.dumps({"gmv_max_promotion_types": [promotion_type]}),
                    },
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "code": 0,
                            "message": "ok",
                            "data": {
                                "list": records,
                                "page_info": {"total_number": len(records), "page": 1, "page_size": 100, "total_page": 1},
                            },
                        }
                    ),
                    status_code=200,
                ),
            )

        output = read(get_source(config=config(), state=None), config(), catalog("gmv_max_campaigns"))

        assert len(output.records) == 1
        assert output.records[0].record.data["campaign_id"] == "campaign-1"


class TestGmvMaxStores(TestCase):
    @HttpMocker()
    def test_emits_available_and_unavailable_stores(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, config())
        mock_stores(
            http_mocker,
            ADVERTISER_ID,
            [
                {"store_id": "111", "is_gmv_max_available": True},
                {"store_id": "222", "is_gmv_max_available": False},
            ],
        )

        output = read(get_source(config=config(), state=None), config(), catalog("gmv_max_stores"))

        assert len(output.records) == 2
        assert {record.record.data["store_id"] for record in output.records} == {"111", "222"}


class TestGmvMaxProductReports(TestCase):
    @HttpMocker()
    def test_only_requests_available_stores_and_flattens_metrics(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, config())
        mock_stores(
            http_mocker,
            ADVERTISER_ID,
            [
                {"store_id": "111", "is_gmv_max_available": True},
                {"store_id": "222", "is_gmv_max_available": False},
            ],
        )
        report_request = mock_report(http_mocker, ADVERTISER_ID, "111", PRODUCT_METRICS, "PRODUCT", "c1")

        output = read(
            get_source(config=config(), state=None),
            config(),
            catalog("gmv_max_product_campaign_reports_daily"),
        )

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["store_id"] == "111"
        assert record["campaign_id"] == "c1"
        assert record["stat_time_day"] == "2024-01-01 00:00:00"
        assert record["metrics"]["orders"] is None
        # HttpMocker fails on unmatched requests, so this also proves store 222 was not queried.
        http_mocker.assert_number_of_calls(report_request, 1)

    @HttpMocker()
    def test_uses_each_parent_advertiser_for_store_reports(self, http_mocker: HttpMocker):
        cfg = config()
        http_mocker.get(
            HttpRequest(
                url=f"{BASE_URL}oauth2/advertiser/get/",
                query_params={"secret": cfg["credentials"]["secret"], "app_id": cfg["credentials"]["app_id"]},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "code": 0,
                        "message": "ok",
                        "data": {"list": [{"advertiser_id": ADVERTISER_ID}, {"advertiser_id": "872746382649"}]},
                    }
                ),
                status_code=200,
            ),
        )
        mock_stores(http_mocker, ADVERTISER_ID, [{"store_id": "111", "is_gmv_max_available": True}])
        mock_stores(http_mocker, "872746382649", [{"store_id": "222", "is_gmv_max_available": True}])
        mock_report(http_mocker, ADVERTISER_ID, "111", PRODUCT_METRICS, "PRODUCT", "c1")
        mock_report(http_mocker, "872746382649", "222", PRODUCT_METRICS, "PRODUCT", "c2")

        output = read(
            get_source(config=cfg, state=None),
            cfg,
            catalog("gmv_max_product_campaign_reports_daily"),
        )

        assert len(output.records) == 2
        assert {(record.record.data["store_id"], record.record.data["campaign_id"]) for record in output.records} == {
            ("111", "c1"),
            ("222", "c2"),
        }


class TestGmvMaxLiveReports(TestCase):
    @HttpMocker()
    def test_uses_live_filtering_and_metrics(self, http_mocker: HttpMocker):
        mock_advertisers_slices(http_mocker, config())
        mock_stores(http_mocker, ADVERTISER_ID, [{"store_id": "111", "is_gmv_max_available": True}])
        mock_report(http_mocker, ADVERTISER_ID, "111", LIVE_METRICS, "LIVE", "c1")

        output = read(
            get_source(config=config(), state=None),
            config(),
            catalog("gmv_max_live_campaign_reports_daily"),
        )

        assert len(output.records) == 1
        assert output.records[0].record.data["campaign_id"] == "c1"
