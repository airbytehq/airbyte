# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API_URL = "https://api.mention.net/api"


@pytest.mark.parametrize(
    "stream_name, expected_ids",
    [
        ("account_me", ["account-1"]),
        ("alert", ["alert-1", "alert-2"]),
        ("mention", ["mention-1", "mention-2"]),
    ],
)
def test_read_uses_bearer_authentication(
    stream_name: str, expected_ids: list[str], config: dict[str, str], manifest_path: Path, requests_mock: Mocker
) -> None:
    requests_mock.get(f"{_API_URL}/accounts/me", complete_qs=True, json={"account": {"id": "account-1"}})
    requests_mock.get(
        f"{_API_URL}/accounts/account-1/alerts?limit=100",
        complete_qs=True,
        json={
            "alerts": [{"id": "alert-1"}],
            "_links": {"more": {"params": {"cursor": "next-alert"}}},
        },
    )
    requests_mock.get(
        f"{_API_URL}/accounts/account-1/alerts?limit=100&cursor=next-alert",
        complete_qs=True,
        json={"alerts": [{"id": "alert-2"}], "_links": {}},
    )
    for alert_id, mention_id in [("alert-1", "mention-1"), ("alert-2", "mention-2")]:
        requests_mock.get(
            f"{_API_URL}/accounts/account-1/alerts/{alert_id}/mentions?limit=1000",
            complete_qs=True,
            json={"mentions": [{"id": mention_id}], "_links": {}},
        )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=catalog)
    output = read(source, config, catalog)

    # Concurrent substream partitions do not guarantee record or request ordering.
    assert sorted(message.record.data["id"] for message in output.records) == expected_ids
    assert not output.errors
    assert requests_mock.request_history
    for request in requests_mock.request_history:
        assert request.headers["Authorization"] == f"Bearer {config['api_key']}"
    if stream_name == "alert":
        assert [request.qs for request in requests_mock.request_history if request.path.endswith("/alerts")] == [
            {"limit": ["100"]},
            {"limit": ["100"], "cursor": ["next-alert"]},
        ]
    if stream_name == "mention":
        assert sorted(request.path for request in requests_mock.request_history if request.path.endswith("/mentions")) == [
            "/api/accounts/account-1/alerts/alert-1/mentions",
            "/api/accounts/account-1/alerts/alert-2/mentions",
        ]
