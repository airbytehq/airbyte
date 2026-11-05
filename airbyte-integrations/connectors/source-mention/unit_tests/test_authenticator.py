# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_ACCOUNT_ME_URL = "https://api.mention.net/api/accounts/me"
_CONFIG = {"api_key": "test_key", "stats_start_date": "2026-09-01T00:00:00Z"}


def test_api_key_is_sent_as_bearer_token(requests_mock):
    requests_mock.get(_ACCOUNT_ME_URL, json={"account": {"id": "acc1", "name": "x"}})
    catalog = CatalogBuilder().with_stream(
        ConfiguredAirbyteStreamBuilder().with_name("account_me").with_sync_mode(SyncMode.full_refresh)
    ).build()

    output = read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)

    assert output.errors == []
    assert len(requests_mock.request_history) == 1
    request = requests_mock.request_history[0]
    assert request.url == _ACCOUNT_ME_URL
    assert request.headers["Authorization"] == "Bearer test_key"
    assert len(output.records) == 1
