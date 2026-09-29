# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source
from .advetiser_slices import mock_advertisers_slices
from .config_builder import ConfigBuilder


BUYING_TYPES = ["AUCTION", "RESERVATION_TOP_VIEW", "RESERVATION_RF"]

CAMPAIGNS_URL = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"

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

EMPTY_CAMPAIGNS_RESPONSE = {
    "code": 0,
    "message": "ok",
    "data": {
        "list": [],
        "page_info": {"total_number": 0, "page": 1, "page_size": 1000, "total_page": 1},
    },
}


class TestCampaignsStream(TestCase):
    """Tests for the campaigns stream buying_types filter.

    The TikTok Marketing API's /campaign/get/ endpoint defaults to returning
    only AUCTION buying type campaigns unless an explicit buying_types filter
    is provided. RESERVATION_TOP_VIEW cannot be combined with other buying
    types, so the connector must make separate API calls per buying type.
    """

    stream_name = "campaigns"
    advertiser_id = "872746382648"

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self, include_deleted: bool = False):
        config_to_build = ConfigBuilder().with_end_date("2024-01-02")
        if include_deleted:
            config_to_build = config_to_build.with_include_deleted()
        return config_to_build.build()

    def _mock_campaigns_for_all_buying_types(self, http_mocker: HttpMocker, include_deleted: bool = False):
        """Register mocked responses for each buying type partition."""
        for buying_type in BUYING_TYPES:
            if include_deleted:
                filtering = json.dumps({"secondary_status": "CAMPAIGN_STATUS_ALL", "buying_types": [buying_type]})
            else:
                filtering = json.dumps({"buying_types": [buying_type]})
            response = CAMPAIGNS_RESPONSE if buying_type == "AUCTION" else EMPTY_CAMPAIGNS_RESPONSE
            http_mocker.get(
                HttpRequest(
                    url=CAMPAIGNS_URL,
                    query_params={
                        "page_size": 1000,
                        "advertiser_id": self.advertiser_id,
                        "filtering": filtering,
                    },
                ),
                HttpResponse(body=json.dumps(response), status_code=200),
            )

    @HttpMocker()
    def test_read_sends_separate_request_per_buying_type(self, http_mocker: HttpMocker):
        """Each buying type gets its own API call with a single-element buying_types filter."""
        mock_advertisers_slices(http_mocker, self.config())
        self._mock_campaigns_for_all_buying_types(http_mocker, include_deleted=False)

        output = read(get_source(config=self.config(), state=None), self.config(), self.catalog())
        assert len(output.records) == 1
        assert output.records[0].record.data["campaign_id"] == 123456789

    @HttpMocker()
    def test_read_with_include_deleted_sends_status_and_buying_type(self, http_mocker: HttpMocker):
        """With include_deleted=True, each request includes secondary_status alongside the
        single buying_type."""
        mock_advertisers_slices(http_mocker, self.config(include_deleted=True))
        self._mock_campaigns_for_all_buying_types(http_mocker, include_deleted=True)

        output = read(
            get_source(config=self.config(include_deleted=True), state=None),
            self.config(include_deleted=True),
            self.catalog(),
        )
        assert len(output.records) == 1
        assert output.records[0].record.data["campaign_id"] == 123456789
