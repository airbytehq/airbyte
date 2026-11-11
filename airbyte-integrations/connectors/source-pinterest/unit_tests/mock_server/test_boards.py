# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy
import json
import logging

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_analytics_columns, get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


BASE_URL = "https://api.pinterest.com/v5/"
ERROR_MESSAGE = "Try to re-authenticate because current refresh token is not valid."
LOGGER = logging.getLogger(__name__)


def config_with_cache():
    return {
        "start_date": "2026-11-10",
        "credentials": {
            "auth_method": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "OLD_REFRESH",
            "access_token": "OLD_ACCESS",
            "token_expiry_date": "2026-11-20T00:00:00Z",
        },
    }


def reauthorize(config):
    """Mirror useFormOauthAdapter.onDone: merge only spec-mapped OAuth payload keys."""
    result = copy.deepcopy(config)
    spec = get_source(config).spec(LOGGER)
    properties = spec.advanced_auth.oauth_config_specification.complete_oauth_output_specification["properties"]
    payload = {"access_token": "NEW_ACCESS", "refresh_token": "NEW_REFRESH"}
    for key, field in properties.items():
        if key in payload:
            target = result
            path = field["path_in_connector_config"]
            for part in path[:-1]:
                target = target.setdefault(part, {})
            target[path[-1]] = payload[key]
    return result


def request(path, token, query=None):
    return HttpRequest(BASE_URL + path, query_params=query, headers={"Authorization": f"Bearer {token}"})


def response(body, status=200):
    return HttpResponse(json.dumps(body), status_code=status)


def token_request(refresh_token):
    return HttpRequest(
        BASE_URL + "oauth/token",
        headers={"Authorization": "Basic Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ="},
        body=f"grant_type=refresh_token&refresh_token={refresh_token}",
    )


@freeze_time("2026-11-11T12:00:00Z")
@pytest.mark.parametrize("authorization", ["reauth", "cached", "refresh_only"])
def test_boards_authorization(authorization):
    config = config_with_cache()
    token = "OLD_ACCESS"
    if authorization == "reauth":
        config = reauthorize(config)
        token = "NEW_ACCESS"
    elif authorization == "refresh_only":
        del config["credentials"]["access_token"]
        del config["credentials"]["token_expiry_date"]
        token = "REFRESHED_ACCESS"

    with HttpMocker() as http_mocker:
        refresh = token_request(config["credentials"]["refresh_token"])
        http_mocker.post(refresh, response({"access_token": "REFRESHED_ACCESS", "expires_in": 2592000}))
        boards = request("boards", token)
        http_mocker.get(boards, response({"items": [{"id": "board-1"}, {"id": "board-2"}]}))
        analytics_query = {
            "start_date": "2026-11-10",
            "end_date": "2026-11-11",
            "granularity": "DAY",
            "columns": get_analytics_columns(),
        }
        analytics = request("user_account/analytics", token, analytics_query)
        http_mocker.get(analytics, response({"all": {"daily_metrics": [{"date": "2026-11-10"}]}}))
        if authorization == "reauth":
            for path, query in [("boards", None), ("user_account/analytics", analytics_query)]:
                http_mocker.get(request(path, "OLD_ACCESS", query), response({"code": 2, "message": "AuthzRecordNotFound"}, 401))

        source = get_source(config)
        if authorization == "reauth":
            status = source.check(LOGGER, config)
            assert status.status == Status.SUCCEEDED, status
        catalog = CatalogBuilder().with_stream("boards", SyncMode.full_refresh).build()
        output = read(source, config, catalog)
        assert [record.record.data["id"] for record in output.records] == ["board-1", "board-2"]
        http_mocker.assert_number_of_calls(boards, 1)
        http_mocker.assert_number_of_calls(refresh, int(authorization == "refresh_only"))
        if authorization == "reauth":
            http_mocker.assert_number_of_calls(analytics, 1)


@freeze_time("2026-11-11T12:00:00Z")
def test_boards_new_authorization_rejected():
    config = reauthorize(config_with_cache())
    with HttpMocker() as http_mocker:
        boards = request("boards", "NEW_ACCESS")
        http_mocker.get(boards, response({"code": 2, "message": "AuthzRecordNotFound"}, 401))
        catalog = CatalogBuilder().with_stream("boards", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message == ERROR_MESSAGE
        assert output.records == []
        http_mocker.assert_number_of_calls(boards, 1)
