# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_account_me_uses_bearer_authentication(source, config, requests_mock):
    request = requests_mock.get(
        "https://api.mention.net/api/accounts/me",
        request_headers={"Authorization": "Bearer test-api-key"},
        json={"account": {"id": "123"}},
    )
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

    output = read(source, config=config, catalog=catalog)

    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-api-key"
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["123"]
    assert request.call_count == 1
