# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "billable_rates"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestBillableRatesStream(TestCase):
    """Tests for the Harvest 'billable_rates' stream."""

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """Test that connector correctly fetches billable_rates.

        Note: billable_rates is a substream of users, so we need to mock both.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock the parent users stream first
        with open(get_resource_path("http/response/users.json")) as f:
            users_data = json.load(f)

        http_mocker.get(
            HarvestRequestBuilder.users_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(body=json.dumps(users_data), status_code=200),
        )

        # Mock the billable_rates substream for the user
        with open(get_resource_path("http/response/billable_rates.json")) as f:
            response_data = json.load(f)

        # The path will be /users/{user_id}/billable_rates
        # Note: billable_rates doesn't have incremental_sync, so no updated_since parameter
        from airbyte_cdk.test.mock_http import HttpRequest

        user_id = users_data["users"][0]["id"]
        http_mocker.get(
            HttpRequest(
                url=f"https://api.harvestapp.com/v2/users/{user_id}/billable_rates",
                query_params={"per_page": "50"},
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) >= 1
        assert output.records[0].record.stream == _STREAM_NAME
