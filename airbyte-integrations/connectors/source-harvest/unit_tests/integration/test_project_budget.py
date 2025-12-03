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

_STREAM_NAME = "project_budget"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


class TestProjectBudgetStream(TestCase):
    @freeze_time("2024-12-30")
    @HttpMocker()
    def test_unauthorized_error_handling(self, http_mocker: HttpMocker) -> None:
        """Test that connector ignores 401 errors per manifest config."""
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token("invalid_token").with_replication_start_date(datetime(2024, 1, 1)).build()

        http_mocker.get(
            HarvestRequestBuilder.project_budget_endpoint(_ACCOUNT_ID, "invalid_token")
            .with_per_page(50)
            .build(),
            HttpResponse(body=json.dumps({"error": "invalid_token"}), status_code=401),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        log_messages = [log.log.message for log in output.logs]
        assert any("Please ensure your credentials are valid" in msg for msg in log_messages)
