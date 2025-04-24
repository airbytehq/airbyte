# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from advetiser_slices import mock_advertisers_slices
from config_builder import ConfigBuilder
from freezegun import freeze_time
from source_tiktok_marketing import SourceTiktokMarketing

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestAdvertiserAudienceReportsLifetime(TestCase):
    stream_name = "advertisers_audience_reports_lifetime"
    advertiser_id = "872746382648"
    metrics = ["spend", "cpc", "cpm", "impressions", "clicks", "ctr"]

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self, include_deleted: bool = False):
        config = ConfigBuilder().with_end_date("2024-12-12")
        if include_deleted:
            config.with_include_deleted()
        return config.build()

    def _mock_response(self, http_mocker: HttpMocker, include_deleted: bool = False):
        mock_advertisers_slices(http_mocker, self.config())
        query_params = {
            "service_type": "AUCTION",
            "report_type": "AUDIENCE",
            "data_level": "AUCTION_ADVERTISER",
            "dimensions": '["advertiser_id", "gender", "age"]',
            "metrics": str(self.metrics).replace("'", '"'),
            "start_date": self.config()["start_date"],
            "end_date": self.config()["end_date"],
            "lifetime": "true",
            "page_size": 1000,
            "advertiser_id": self.advertiser_id,
        }
        if include_deleted:
            query_params["filters"] = (
                '[{"filter_value": ["STATUS_ALL"], "field_name": "ad_status", "filter_type": "IN"}, {"filter_value": ["STATUS_ALL"], "field_name": "campaign_status", "filter_type": "IN"}, {"filter_value": ["STATUS_ALL"], "field_name": "adgroup_status", "filter_type": "IN"}]'
            )
        http_mocker.get(
            HttpRequest(
                url=f"https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                query_params=query_params,
            ),
            HttpResponse(body=json.dumps(find_template(self.stream_name, __file__)), status_code=200),
        )

    @HttpMocker()
    @freeze_time("2024-12-12")
    def test_basic_read(self, http_mocker: HttpMocker):
        self._mock_response(http_mocker)

        output = read(SourceTiktokMarketing(config=self.config(), catalog=None, state=None), self.config(), self.catalog())
        assert len(output.records) == 2

    @HttpMocker()
    @freeze_time("2024-12-12")
    def test_basic_read_include_deleted(self, http_mocker: HttpMocker):
        self._mock_response(http_mocker, True)

        output = read(
            SourceTiktokMarketing(config=self.config(include_deleted=True), catalog=None, state=None),
            self.config(include_deleted=True),
            self.catalog(),
        )
        assert len(output.records) == 2
