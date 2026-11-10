# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Callable
from urllib.parse import urlsplit

from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_read_currencies_converts_dotnet_dates(get_source: Callable[..., ConcurrentDeclarativeSource], requests_mock: Mocker) -> None:
    config = {
        "tenant_id": "test-tenant",
        "start_date": "2014-01-01T00:00:00Z",
        "credentials": {"auth_type": "oauth2_access_token", "access_token": "test-token"},
    }
    request = requests_mock.get(
        "https://api.xero.com/api.xro/2.0/Currencies?page=1&pageSize=1000",
        complete_qs=True,
        request_headers={"Xero-Tenant-Id": "test-tenant"},
        json={"Currencies": [{"Code": "USD", "Description": "US Dollar", "UpdatedDateUTC": "/Date(1419937200000+0000)/"}]},
    )
    catalog = CatalogBuilder().with_stream("currencies", SyncMode.full_refresh).build()

    output = read(get_source(config=config, catalog=catalog), config=config, catalog=catalog)

    assert [(message.record.stream, message.record.data) for message in output.records] == [
        ("currencies", {"Code": "USD", "Description": "US Dollar", "UpdatedDateUTC": "2014-12-30T11:00:00+00:00"})
    ]
    assert not output.errors
    assert request.call_count == 1
    assert urlsplit(requests_mock.last_request.url).path == "/api.xro/2.0/Currencies"
    assert requests_mock.last_request.headers["Xero-Tenant-Id"] == "test-tenant"
