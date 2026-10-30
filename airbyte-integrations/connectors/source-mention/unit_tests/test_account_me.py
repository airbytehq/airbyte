# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_account_me_uses_bearer_token(requests_mock):
    config = {"api_key": "test-api-key", "stats_start_date": "2025-01-01T00:00:00Z"}
    requests_mock.get("https://api.mention.net/api/accounts/me", json={"account": {"id": 123}})
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

    output = read(get_source(config), config=config, catalog=catalog)

    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-api-key"
    assert output.errors == []
    assert [record.record.data for record in output.records] == [{"id": 123}]
