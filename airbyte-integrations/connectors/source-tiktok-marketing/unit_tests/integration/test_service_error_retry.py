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


CAMPAIGNS_URL = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
ADVERTISER_ID = "872746382648"
AUCTION_FILTER = json.dumps({"buying_types": ["AUCTION"]})

SERVICE_ERROR_RESPONSE = {"code": 50000, "message": "System error.", "data": {}}
CAMPAIGNS_RESPONSE = {
    "code": 0,
    "message": "ok",
    "data": {
        "list": [
            {
                "campaign_id": 123456789,
                "campaign_name": "Test Campaign",
                "advertiser_id": 872746382648,
                "budget": 100.0,
                "budget_mode": "BUDGET_MODE_DAY",
                "secondary_status": "CAMPAIGN_STATUS_ENABLE",
                "objective_type": "TRAFFIC",
                "create_time": "2024-01-01 00:00:00",
                "modify_time": "2024-01-01 12:00:00",
                "is_new_structure": True,
                "campaign_type": "REGULAR_CAMPAIGN",
            }
        ],
        "page_info": {"total_number": 1, "page": 1, "page_size": 1000, "total_page": 1},
    },
}


class TestServiceErrorRetry(TestCase):
    @HttpMocker()
    def test_campaigns_retries_http_200_service_error_and_emits_records(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_end_date("2024-01-02").build()
        catalog = CatalogBuilder().with_stream(name="campaigns", sync_mode=SyncMode.full_refresh).build()
        mock_advertisers_slices(http_mocker, config)

        http_mocker.get(
            HttpRequest(
                url=CAMPAIGNS_URL,
                query_params={
                    "page_size": 1000,
                    "advertiser_id": ADVERTISER_ID,
                    "filtering": AUCTION_FILTER,
                },
            ),
            [
                HttpResponse(body=json.dumps(SERVICE_ERROR_RESPONSE), status_code=200),
                HttpResponse(body=json.dumps(CAMPAIGNS_RESPONSE), status_code=200),
            ],
        )

        for buying_type in ("RESERVATION_TOP_VIEW", "RESERVATION_RF"):
            http_mocker.get(
                HttpRequest(
                    url=CAMPAIGNS_URL,
                    query_params={
                        "page_size": 1000,
                        "advertiser_id": ADVERTISER_ID,
                        "filtering": json.dumps({"buying_types": [buying_type]}),
                    },
                ),
                HttpResponse(
                    body=json.dumps({"code": 0, "message": "ok", "data": {"list": [], "page_info": {"total_page": 1}}}),
                    status_code=200,
                ),
            )

        output = read(get_source(config=config, state=None), config, catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["campaign_id"] == 123456789
