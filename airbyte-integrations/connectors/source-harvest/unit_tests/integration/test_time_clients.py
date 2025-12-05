# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

from freezegun import freeze_time
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder


_STREAM_NAME = "time_clients"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


class TestTimeClientsStream(TestCase):
    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        # Use a recent start date to minimize year slices
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )
        with open(get_resource_path("http/response/time_clients.json")) as f:
            response_data = json.load(f)
        http_mocker.get(
            HarvestRequestBuilder.time_clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps(response_data), status_code=200),
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        assert len(output.records) == 1
        assert output.records[0].record.data["client_id"] == 1
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

        # ASSERT: Transformation should add 'from' and 'to' date fields to records
        record_data = output.records[0].record.data
        assert "from" in record_data, "Transformation should add 'from' field to record"
        assert "to" in record_data, "Transformation should add 'to' field to record"
        assert record_data["from"] == "20240101", "from field should match partition start"
        assert record_data["to"] == "20241230", "to field should match partition end"

    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        # Use a recent start date to minimize year slices
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )
        http_mocker.get(
            HarvestRequestBuilder.time_clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(
                body=json.dumps({"results": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}),
                status_code=200,
            ),
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        # ASSERT: No records but no errors
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token("invalid_token")
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )

        http_mocker.get(
            HarvestRequestBuilder.time_clients_endpoint(_ACCOUNT_ID, "invalid_token")
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps({"error": "invalid_token"}), status_code=401),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_forbidden_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 403 errors per manifest config."""
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )

        http_mocker.get(
            HarvestRequestBuilder.time_clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps({"error": "forbidden"}), status_code=403),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_not_found_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 404 errors per manifest config."""
        config = (
            ConfigBuilder()
            .with_account_id(_ACCOUNT_ID)
            .with_api_token(_API_TOKEN)
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )

        http_mocker.get(
            HarvestRequestBuilder.time_clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_from_date("20240101")
            .with_to_date("20241230")
            .build(),
            HttpResponse(body=json.dumps({"error": "not_found"}), status_code=404),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
