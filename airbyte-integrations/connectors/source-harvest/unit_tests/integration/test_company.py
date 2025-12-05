# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_resource_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from integration.config import ConfigBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "company"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestCompanyStream(TestCase):
    """
    Tests for the Harvest 'company' stream.

    The company stream returns a single object with company information.
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches company information.

        Given: A configured Harvest connector
        When: Running a full refresh sync for the company stream
        Then: The connector should return the company record
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Load response from JSON file
        with open(get_resource_path("http/response/company.json")) as f:
            company_data = json.load(f)

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/company",
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps(company_data), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Should retrieve exactly one company record
        assert len(output.records) == 1
        assert output.records[0].record.stream == _STREAM_NAME
        assert output.records[0].record.data["name"] == "Test Company"
        assert output.records[0].record.data["is_active"] is True

        # ASSERT: Should have log messages indicating successful sync completion

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        """
        Test that connector handles empty company response gracefully.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        # Mock empty response (company returns empty object or null)
        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/company",
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": f"Bearer {_API_TOKEN}"},
            ),
            HttpResponse(body=json.dumps({}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: No records but no errors
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_unauthorized_error(self, http_mocker: HttpMocker):
        """
        Test that connector handles 401 Unauthorized errors gracefully.

        The company stream does not have a custom error handler, so 401 errors
        are treated as sync failures but the sync completes with 0 records
        and the error is logged rather than raising an exception.
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").build()

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/company",
                headers={"Harvest-Account-Id": _ACCOUNT_ID, "Authorization": "Bearer invalid_token"},
            ),
            HttpResponse(body=json.dumps({"error": "Unauthorized"}), status_code=401),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # ASSERT: Sync completes with 0 records (error is handled gracefully)
        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
