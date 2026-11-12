# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_ORG_URL = "https://api.linkedin.com/rest/organizations/12345678"
_TOKEN_CREDENTIALS = {"auth_method": "access_token", "access_token": "legacy_token"}
_OAUTH_CREDENTIALS = {"auth_method": "oAuth2.0", "client_id": "id", "client_secret": "secret", "refresh_token": "refresh"}


@pytest.mark.parametrize(
    "config, expected",
    [
        pytest.param(
            {"org_id": 12345678, "credentials": _TOKEN_CREDENTIALS},
            {"org_id": "12345678", "credentials": _TOKEN_CREDENTIALS},
            id="integer org_id from before 1.0.0",
        ),
        pytest.param(
            {"org_id": "12345678", "access_token": "legacy_token"},
            {"org_id": "12345678", "credentials": _TOKEN_CREDENTIALS},
            id="top-level access_token",
        ),
        pytest.param(
            {"org_id": "12345678", "credentials": {}, "access_token": "legacy_token"},
            {"org_id": "12345678", "credentials": _TOKEN_CREDENTIALS},
            id="empty credentials and a top-level access_token",
        ),
        pytest.param(
            # Without auth_method the Python connector used the top-level token.
            {"org_id": "12345678", "credentials": {"access_token": "inner"}, "access_token": "legacy_token"},
            {"org_id": "12345678", "credentials": _TOKEN_CREDENTIALS},
            id="credentials without auth_method and a top-level access_token",
        ),
        pytest.param(
            {"org_id": "12345678", "credentials": _OAUTH_CREDENTIALS, "access_token": "stray"},
            {"org_id": "12345678", "credentials": _OAUTH_CREDENTIALS, "access_token": "stray"},
            id="valid OAuth credentials keep an unused top-level key",
        ),
        pytest.param(
            {"org_id": "12345678", "credentials": _OAUTH_CREDENTIALS},
            {"org_id": "12345678", "credentials": _OAUTH_CREDENTIALS},
            id="valid OAuth config is unchanged",
        ),
        pytest.param(
            {"org_id": "12345678", "credentials": "not an object", "access_token": "legacy_token"},
            {"org_id": "12345678", "credentials": "not an object", "access_token": "legacy_token"},
            id="malformed credentials are left for spec validation",
        ),
    ],
)
def test_config_migrations(config, expected):
    # The CDK migrates a shallow copy, so nested dicts change in place: keep the parametrized values intact.
    assert get_source(deepcopy(config))._config == expected


@pytest.mark.parametrize(
    "config",
    [
        {"org_id": 12345678, "credentials": {"auth_method": "access_token", "access_token": "legacy_token"}},
        {"org_id": "12345678", "access_token": "legacy_token"},
    ],
)
def test_legacy_configs_still_sync(config):
    catalog = CatalogBuilder().with_stream("organization_lookup", SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(_ORG_URL, json={"id": 12345678, "localizedName": "Test Org"})
        output = read(get_source(deepcopy(config)), deepcopy(config), catalog)

    assert output.errors == []
    assert len(output.records) == 1
    assert endpoint.last_request.headers["Authorization"] == "Bearer legacy_token"
