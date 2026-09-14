# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "org_id": "12345678",
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
    "start_date": "2023-10-31T00:00:00Z",
    "time_granularity_type": "DAY",
}

_BASE_URL = "https://api.linkedin.com/rest"

_STREAMS = [
    pytest.param("organization_lookup", "GET", "/organizations/12345678", {"id": 12345678, "localizedName": "Test Org"}),
    pytest.param("follower_statistics", "GET", "/organizationalEntityFollowerStatistics", {"elements": []}),
    pytest.param("share_statistics", "GET", "/organizationalEntityShareStatistics", {"elements": []}),
    pytest.param("total_follower_count", "GET", "/networkSizes/urn:li:organization:12345678", {"firstDegreeSize": 10}),
    pytest.param("follower_statistics_time_bound", "GET", "/organizationalEntityFollowerStatistics", {"elements": []}),
    pytest.param("share_statistics_time_bound", "GET", "/organizationalEntityShareStatistics", {"elements": []}),
]


@pytest.mark.parametrize("stream_name, method, path, response", _STREAMS)
def test_requests_use_linkedin_api_version(stream_name: str, method: str, path: str, response: dict[str, Any]) -> None:
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(method, f"{_BASE_URL}{path}", json=response)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        read(get_source(_CONFIG), _CONFIG, catalog)

        assert len(mocker.request_history) >= 1
        api_requests = [request for request in mocker.request_history if request.hostname == "api.linkedin.com"]
        assert api_requests
        assert all(request.headers["Linkedin-Version"] == "202608" for request in api_requests)


def _linkedin_version_values(value: Any):
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key == "Linkedin-Version":
                yield nested_value
            else:
                yield from _linkedin_version_values(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _linkedin_version_values(nested_value)


def test_manifest_uses_only_linkedin_api_version_202608() -> None:
    with MANIFEST_PATH.open() as manifest_file:
        manifest = yaml.safe_load(manifest_file)

    versions = list(_linkedin_version_values(manifest))
    assert versions
    assert all(version == "202608" for version in versions)
