# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time

from unit_tests.conftest import get_source, get_resource_path
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder

_STREAM_NAME = "expenses_team"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


class TestExpensesTeamStream(TestCase):
    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        # Use a recent start date to minimize year slices
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).with_replication_start_date(datetime(2024, 1, 1)).build()
        with open(get_resource_path("http/response/expenses_team.json")) as f:
            response_data = json.load(f)
        http_mocker.get(
            HarvestRequestBuilder.expenses_team_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps(response_data), status_code=200)
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        assert len(output.records) == 1
        assert output.records[0].record.data["user_id"] == 1
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        # Use a recent start date to minimize year slices
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).with_replication_start_date(datetime(2024, 1, 1)).build()
        http_mocker.get(
            HarvestRequestBuilder.expenses_team_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps({"results": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}), status_code=200)
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        assert len(output.records) == 0
