# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from ..conftest import get_source
from .advetiser_slices import mock_advertisers_slices
from .config_builder import ConfigBuilder


ADS_URL = "https://business-api.tiktok.com/open_api/v1.3/ad/get/"
AD_RESPONSE = {
    "code": 0,
    "message": "ok",
    "data": {
        "list": [
            {
                "advertiser_id": 872746382648,
                "ad_id": 123456789,
                "modify_time": "2024-01-02 04:00:00",
            }
        ],
        "page_info": {"total_number": 1, "page": 1, "page_size": 1000, "total_page": 1},
    },
}


class TestAdsStream(TestCase):
    advertiser_id = "872746382648"

    def catalog(self):
        return CatalogBuilder().with_stream(name="ads", sync_mode=SyncMode.incremental).build()

    def config(self, include_deleted: bool = False):
        config = ConfigBuilder().build()
        config["start_date"] = "2016-09-01"
        if include_deleted:
            config["include_deleted"] = True
        return config

    def state(self, cursor: str):
        return (
            StateBuilder()
            .with_stream_state(
                stream_name="ads",
                state={
                    "states": [
                        {
                            "partition": {"advertiser_id": self.advertiser_id, "parent_slice": {}},
                            "cursor": {"modify_time": cursor},
                        }
                    ]
                },
            )
            .build()
        )

    def mock_ads(self, http_mocker: HttpMocker, modified_after: str, include_deleted: bool = False):
        filtering = {"modified_after": modified_after}
        if include_deleted:
            filtering["secondary_status"] = "AD_STATUS_ALL"
        http_mocker.get(
            HttpRequest(
                url=ADS_URL,
                query_params={
                    "page_size": 1000,
                    "advertiser_id": self.advertiser_id,
                    "filtering": json.dumps(filtering),
                },
            ),
            HttpResponse(body=json.dumps(AD_RESPONSE), status_code=200),
        )

    @HttpMocker()
    def test_read_with_state_uses_state_cursor_for_modified_after(self, http_mocker: HttpMocker):
        config = self.config()
        cursor = "2024-01-02T03:04:05Z"
        mock_advertisers_slices(http_mocker, config)
        self.mock_ads(http_mocker, "2024-01-02 03:04:05")

        output = read(
            source=get_source(config=config, state=self.state(cursor)),
            config=config,
            catalog=self.catalog(),
            state=self.state(cursor),
        )

        assert len(output.records) == 1

    @HttpMocker()
    def test_read_without_state_uses_config_start_date_for_modified_after(self, http_mocker: HttpMocker):
        config = self.config()
        mock_advertisers_slices(http_mocker, config)
        self.mock_ads(http_mocker, "2016-09-01 00:00:00")

        output = read(get_source(config=config, state=None), config, self.catalog())

        assert len(output.records) == 1

    @HttpMocker()
    def test_read_with_include_deleted_sends_secondary_status(self, http_mocker: HttpMocker):
        config = self.config(include_deleted=True)
        mock_advertisers_slices(http_mocker, config)
        self.mock_ads(http_mocker, "2016-09-01 00:00:00", include_deleted=True)

        output = read(get_source(config=config, state=None), config, self.catalog())

        assert len(output.records) == 1
