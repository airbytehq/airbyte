#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Tests for URL routing between the standard `{domain}.atlassian.net` endpoint
and the Atlassian Service Account Platform API Gateway at `api.atlassian.com`.
"""

import pytest
import responses
from conftest import find_stream, read_full_refresh


_CLOUD_ID = "1a11d016-8984-4c3e-b9ab-142dd06acb1b"
_DOMAIN = "airbyteio.atlassian.net"


def _config(cloud_id: str | None = None) -> dict:
    config = {
        "api_token": "token",
        "domain": _DOMAIN,
        "email": "email@email.com",
        "start_date": "2021-01-01T00:00:00Z",
    }
    if cloud_id is not None:
        config["cloud_id"] = cloud_id
    return config


@pytest.mark.parametrize(
    "cloud_id,expected_url_prefix",
    [
        pytest.param(None, f"https://{_DOMAIN}/rest/api/3/", id="domain_route_when_cloud_id_not_set"),
        pytest.param(
            _CLOUD_ID,
            f"https://api.atlassian.com/ex/jira/{_CLOUD_ID}/rest/api/3/",
            id="api_atlassian_gateway_route_when_cloud_id_set",
        ),
    ],
)
@responses.activate
def test_rest_api_v3_url_routing(cloud_id, expected_url_prefix, application_roles_response):
    config = _config(cloud_id)
    responses.add(
        responses.GET,
        f"{expected_url_prefix}applicationrole",
        json=application_roles_response,
    )

    stream = find_stream("application_roles", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(expected_url_prefix)


@pytest.mark.parametrize(
    "cloud_id,expected_url_prefix",
    [
        pytest.param(None, f"https://{_DOMAIN}/rest/agile/1.0/", id="domain_route_when_cloud_id_not_set"),
        pytest.param(
            _CLOUD_ID,
            f"https://api.atlassian.com/ex/jira/{_CLOUD_ID}/rest/agile/1.0/",
            id="api_atlassian_gateway_route_when_cloud_id_set",
        ),
    ],
)
@responses.activate
def test_agile_api_v1_url_routing(cloud_id, expected_url_prefix, boards_response):
    config = _config(cloud_id)
    responses.add(
        responses.GET,
        f"{expected_url_prefix}board?maxResults=50",
        json=boards_response,
    )

    stream = find_stream("boards", config)
    records = list(read_full_refresh(stream))

    assert len(records) >= 1
    assert responses.calls[0].request.url.startswith(expected_url_prefix)
