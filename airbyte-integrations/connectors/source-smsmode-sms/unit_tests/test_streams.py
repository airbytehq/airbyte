# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_key": "fake-key"}
_CONNECTOR_ROOT = Path("/airbyte/integration_code/source_declarative_manifest")
if not _CONNECTOR_ROOT.exists():
    _CONNECTOR_ROOT = Path(__file__).parent.parent


def get_source(config: dict[str, str]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_CONNECTOR_ROOT / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


@pytest.mark.parametrize(
    "stream_name,url,id_field",
    [
        pytest.param("messages", "https://rest.smsmode.com/sms/v1/messages", "messageId", id="messages"),
        pytest.param(
            "consumptions",
            "https://rest.smsmode.com/commons/v1/consumptions",
            "consumptionId",
            id="consumptions",
        ),
    ],
)
def test_stream_pagination_and_authentication(requests_mock: Mocker, stream_name: str, url: str, id_field: str) -> None:
    first_page = [{id_field: f"{stream_name}-{index}"} for index in range(100)]
    second_page = [{id_field: f"{stream_name}-100"}]
    requests_mock.get(url, [{"json": {"items": first_page}}, {"json": {"items": second_page}}])

    output = read_stream(stream_name)

    expected_ids = [record[id_field] for record in [*first_page, *second_page]]
    emitted_ids = [message.record.data[id_field] for message in output.records]
    assert emitted_ids == expected_ids
    assert len(requests_mock.request_history) == 2

    first_query = parse_qs(urlsplit(requests_mock.request_history[0].url).query)
    second_query = parse_qs(urlsplit(requests_mock.request_history[1].url).query)
    assert first_query.get("pageSize") == ["100"]
    assert "page" not in first_query
    assert second_query.get("pageSize") == ["100"]
    assert second_query.get("page") == ["2"]
    assert all(request.headers["X-Api-Key"] == _CONFIG["api_key"] for request in requests_mock.request_history)
