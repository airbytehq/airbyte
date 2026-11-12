# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_API_KEY = "test-mention-token"
_CONFIG = {"api_key": _API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}


def test_account_me_read_sends_api_key_as_bearer_token():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(
                url="https://api.mention.net/api/accounts/me",
                headers={"Authorization": f"Bearer {_API_KEY}"},
            ),
            HttpResponse(body='{"account": {"id": "acc-123", "name": "Acme"}}', status_code=200),
        )

        catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

    assert [record.record.data["id"] for record in output.records] == ["acc-123"]
    assert not output.errors
