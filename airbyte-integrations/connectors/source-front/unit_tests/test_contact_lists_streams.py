# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the contact-group streams on `source-front`.

Front deprecated the `contact_groups` endpoints on 2025-09-01 in favour of the
drop-in `contact_lists` endpoints. These tests verify that the `contact_groups`,
`teammates_contact_groups` and `teams_contact_groups` streams request the
`contact_lists` paths and emit the records from the `_results` envelope.
"""

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test-token", "start_date": "2024-01-01T00:00:00Z", "page_limit": "50"}
_BASE_URL = "https://api2.frontapp.com"


def _get_source():
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(_get_source(), _CONFIG, catalog)


def _contact_list(list_id: str) -> dict:
    return {
        "_links": {"self": f"{_BASE_URL}/contact_lists/{list_id}"},
        "id": list_id,
        "name": f"List {list_id}",
        "is_private": False,
    }


def _page(items: list, next_url: str | None = None) -> dict:
    return {"_pagination": {"next": next_url}, "_results": items}


@pytest.mark.parametrize(
    "stream_name,parent_path,parent_id,expected_path",
    [
        pytest.param("contact_groups", None, None, "/contact_lists", id="contact_groups"),
        pytest.param("teammates_contact_groups", "/teammates", "tea_1", "/teammates/tea_1/contact_lists", id="teammates_contact_groups"),
        pytest.param("teams_contact_groups", "/teams", "tim_1", "/teams/tim_1/contact_lists", id="teams_contact_groups"),
    ],
)
def test_contact_group_streams_read_from_contact_lists_endpoints(stream_name, parent_path, parent_id, expected_path):
    with requests_mock.Mocker() as mocker:
        if parent_path:
            mocker.get(f"{_BASE_URL}{parent_path}", json=_page([{"id": parent_id}]))
        mocker.get(
            f"{_BASE_URL}{expected_path}",
            [
                {"json": _page([_contact_list("grp_1")], next_url=f"{_BASE_URL}{expected_path}?page_token=2")},
                {"json": _page([_contact_list("grp_2")])},
            ],
        )
        output = _read_stream(stream_name)

        requested_paths = [request.path for request in mocker.request_history]

    assert output.errors == []
    assert requested_paths.count(expected_path) == 2
    assert not any("contact_groups" in path for path in requested_paths)
    assert [record.record.data["id"] for record in output.records] == ["grp_1", "grp_2"]
