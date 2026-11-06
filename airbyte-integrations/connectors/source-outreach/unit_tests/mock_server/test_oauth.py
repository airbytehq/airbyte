# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from urllib.parse import urlencode

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


TOKEN_URL = "https://api.outreach.io/oauth/token"
MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"
CONFIG = {
    "client_id": "client",
    "client_secret": "secret",
    "refresh_token": "refresh-0",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2025-01-01T00:00:00Z",
}
PARAMS = {
    "count": "false",
    "sort": "updatedAt",
    "page[size]": "100",
    "newFilterSyntax": "true",
    "filter[updatedAt][gte]": "2025-01-01T00:00:00.000Z",
}


def refresh_request(token):
    return HttpRequest(
        TOKEN_URL, body=urlencode({"grant_type": "refresh_token", "client_id": "client", "client_secret": "secret", "refresh_token": token})
    )


def token_response(number):
    return HttpResponse(json.dumps({"access_token": f"access-{number}", "refresh_token": f"refresh-{number}", "expires_in": 3600}))


def page_request(token, page=None):
    params = dict(PARAMS)
    if page:
        params["page[after]"] = page
    return HttpRequest(MAILINGS_URL, query_params=params, headers={"Authorization": f"Bearer {token}"})


def page_response(ids, next_page=None):
    return HttpResponse(
        json.dumps(
            {
                "data": [{"id": i, "attributes": {"updatedAt": "2025-01-01T00:00:00.000Z"}} for i in ids],
                "links": {"next": f'{MAILINGS_URL}?{urlencode(dict(PARAMS, **{"page[after]": next_page}))}' if next_page else None},
            }
        )
    )


def read_mailings(config=None):
    config = deepcopy(config or CONFIG)
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    return read(get_source(config), config=config, catalog=catalog)


def controls(capsys):
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    return [message["control"]["connectorConfig"]["config"] for message in messages if message.get("type") == "CONTROL"]


def test_refresh_rotates_across_pages_and_next_sync(capsys):
    with freeze_time("2025-01-02T00:00:00Z") as clock, HttpMocker() as http:
        first_refresh = refresh_request("refresh-0")
        second_refresh = refresh_request("refresh-1")
        http.post(first_refresh, [token_response(1), HttpResponse(json.dumps({"error": "invalid_grant"}), 400)])
        http.post(second_refresh, token_response(2))
        first_page = page_request("access-1")
        second_page = page_request("access-2", "1")
        response = page_response([1], "1")

        def delayed_page(request, context):
            clock.tick(3601)
            return response.body.encode()

        http.get(first_page, HttpResponse(delayed_page))
        http.get(second_page, page_response([2]))
        output = read_mailings()

        http.assert_number_of_calls(first_refresh, 1)
        http.assert_number_of_calls(second_refresh, 1)
        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        updates = controls(capsys)
        assert [config["refresh_token"] for config in updates] == ["refresh-1", "refresh-2"]
        assert updates[-1]["access_token"] == "access-2"

        clock.tick(3601)
        third_refresh = refresh_request("refresh-2")
        http.post(third_refresh, token_response(3))
        http.get(page_request("access-3"), page_response([3]))
        next_output = read_mailings(updates[-1])
        assert next_output.errors == [], next_output.get_formatted_error_message()
        assert [record.record.data["id"] for record in next_output.records] == [3]
        http.assert_number_of_calls(third_refresh, 1)
        assert controls(capsys)[-1]["refresh_token"] == "refresh-3"


@pytest.mark.parametrize(
    "error_id,rejected_again", [("expiredAccessToken", False), ("expiredAccessToken", True), ("invalidAccessToken", False)]
)
def test_401_refresh_is_targeted_and_bounded(error_id, rejected_again, capsys):
    with freeze_time("2025-01-02T00:00:00Z") as clock, HttpMocker() as http:
        http.post(refresh_request("refresh-0"), token_response(1))
        first_response = page_response([1], "1")

        def delayed_page(request, context):
            clock.tick(3599)
            return first_response.body.encode()

        http.get(page_request("access-1"), HttpResponse(delayed_page))
        error = HttpResponse(json.dumps({"errors": [{"id": error_id, "detail": "Please get a new access token and try again."}]}), 401)
        http.get(page_request("access-1", "1"), error)
        if error_id == "expiredAccessToken":
            second_refresh = refresh_request("refresh-1")
            http.post(second_refresh, token_response(2))
            http.get(page_request("access-2", "1"), error if rejected_again else page_response([2]))

        output = read_mailings()

        if error_id == "expiredAccessToken" and not rejected_again:
            assert output.errors == [], output.get_formatted_error_message()
            assert [record.record.data["id"] for record in output.records] == [1, 2]
        else:
            assert output.errors
            assert output.errors[0].trace.error.failure_type.value == "config_error"
            assert [record.record.data["id"] for record in output.records] == [1]
        if error_id == "expiredAccessToken":
            http.assert_number_of_calls(second_refresh, 1)
            assert controls(capsys)[-1]["refresh_token"] == "refresh-2"


def test_empty_page_stops_and_persists_rotation(capsys):
    with freeze_time("2025-01-02T00:00:00Z"), HttpMocker() as http:
        http.post(refresh_request("refresh-0"), token_response(1))
        http.get(page_request("access-1"), page_response([]))
        output = read_mailings()
        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert controls(capsys)[-1]["refresh_token"] == "refresh-1"
