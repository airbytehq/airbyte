# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase

import freezegun
import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import HarvestRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "clients"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestConcurrencyLevel(TestCase):
    """
    Tests for the concurrency_level configuration.

    These tests verify:
    - The connector loads and syncs correctly with concurrency_level configured
    - The num_workers config parameter is accepted and used
    - Rate limit handling (429 retry) works correctly
    """

    @HttpMocker()
    def test_sync_with_concurrency(self, http_mocker: HttpMocker):
        """
        Test that the connector syncs correctly with concurrency_level configured.

        Given: A manifest with ConcurrencyLevel configured
        When: Running a full refresh sync
        Then: The connector should complete successfully and return records
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "clients": [
                            {
                                "id": 101,
                                "name": "Test Client",
                                "is_active": True,
                                "currency": "USD",
                                "created_at": "2023-01-15T10:00:00Z",
                                "updated_at": "2023-06-20T15:30:00Z",
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "total_entries": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 101

    @HttpMocker()
    def test_sync_with_custom_num_workers(self, http_mocker: HttpMocker):
        """
        Test that the connector accepts and uses the num_workers config parameter.

        Given: A config with num_workers set to 3
        When: Running a full refresh sync
        Then: The connector should complete successfully (num_workers is accepted without error)
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()
        config["num_workers"] = 3

        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "clients": [
                            {
                                "id": 201,
                                "name": "Custom Workers Client",
                                "is_active": True,
                                "currency": "EUR",
                                "created_at": "2023-02-01T00:00:00Z",
                                "updated_at": "2023-02-01T00:00:00Z",
                            }
                        ],
                        "per_page": 50,
                        "total_pages": 1,
                        "total_entries": 1,
                        "page": 1,
                        "links": {},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 201

    def test_manifest_concurrency_level_structure(self):
        """
        Test that the manifest contains a properly structured ConcurrencyLevel.

        Given: The connector manifest with concurrency_level configured
        When: Loading and parsing the manifest
        Then: The concurrency_level should have ConcurrencyLevel type with correct defaults
        """
        manifest_path = Path(__file__).parent.parent.parent / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())

        assert "concurrency_level" in manifest, "concurrency_level should be defined in the manifest"
        concurrency = manifest["concurrency_level"]
        assert concurrency["type"] == "ConcurrencyLevel"
        assert concurrency["max_concurrency"] == 10
        assert "config.get('num_workers', 4)" in concurrency["default_concurrency"]

    @HttpMocker()
    def test_rate_limit_429_retry(self, http_mocker: HttpMocker):
        """
        Test that 429 rate limit responses are handled correctly.

        Given: An API that returns 429 followed by a successful response
        When: Running a sync
        Then: The connector should retry and eventually succeed
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            HarvestRequestBuilder.clients_endpoint(_ACCOUNT_ID, _API_TOKEN)
            .with_per_page(50)
            .with_updated_since("2021-01-01T00:00:00Z")
            .build(),
            [
                HttpResponse(
                    body=json.dumps({"error": "rate_limit_exceeded"}),
                    status_code=429,
                    headers={"Retry-After": "1"},
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "clients": [
                                {
                                    "id": 301,
                                    "name": "Rate Limited Client",
                                    "is_active": True,
                                    "currency": "USD",
                                    "created_at": "2023-03-01T00:00:00Z",
                                    "updated_at": "2023-03-01T00:00:00Z",
                                }
                            ],
                            "per_page": 50,
                            "total_pages": 1,
                            "page": 1,
                            "links": {},
                        }
                    ),
                    status_code=200,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 301

    def test_num_workers_in_spec(self):
        """
        Test that the num_workers parameter is present in the connector spec.

        Given: The connector manifest with num_workers defined in spec
        When: Getting the connector spec
        Then: num_workers should be present with correct type, default, min, and max
        """
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()
        source = get_source(config=config)
        spec = source.spec(logger=None)
        properties = spec.connectionSpecification["properties"]

        assert "num_workers" in properties, "num_workers should be in the connector spec"
        num_workers_spec = properties["num_workers"]
        assert num_workers_spec["type"] == "integer"
        assert num_workers_spec["default"] == 4
        assert num_workers_spec["minimum"] == 2
        assert num_workers_spec["maximum"] == 10
