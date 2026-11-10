# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test-token", "org_id": "test-org", "project_id": "test-project", "start_date": "2024-01-01T00:00:00Z"}
URL = "https://circleci.com/api/v2/context"
RECORD = {"id": "context-1", "created_at": "2024-02-01T00:00:00.000Z"}


def read_context(expect_error=False):
    catalog = CatalogBuilder().with_stream("context", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expect_error)


@pytest.mark.parametrize("items", [[], [{**RECORD, "id": "context-2"}]], ids=["empty-last-page", "two-pages"])
def test_context_pagination(items):
    first = HttpRequest(url=URL, query_params={"owner-id": "test-org"})
    second = HttpRequest(url=URL, query_params={"owner-id": "test-org", "page-token": "next-context"})
    with HttpMocker() as http_mocker:
        http_mocker.get(first, HttpResponse(body=json.dumps({"items": [RECORD], "next_page_token": "next-context"})))
        http_mocker.get(second, HttpResponse(body=json.dumps({"items": items})))
        output = read_context()
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)

    assert [record.record.data["id"] for record in output.records] == ["context-1"] + [item["id"] for item in items]
    assert not output.errors


@pytest.mark.parametrize(
    "statuses, expected_ids, expected_waits",
    [([429, 429, 429, 429], [], [5.0, 9.0, 17.0]), ([429, 429, 200], ["context-1"], [5.0, 9.0])],
    ids=["exhausted", "recovered"],
)
def test_context_rate_limits(statuses, expected_ids, expected_waits, backoff_waits):
    request = HttpRequest(url=URL, query_params={"owner-id": "test-org"})
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                HttpResponse(
                    body=json.dumps({"items": [RECORD]} if status == 200 else {"message": "Too Many Requests"}), status_code=status
                )
                for status in statuses
            ],
        )
        output = read_context(expect_error=not expected_ids)
        http_mocker.assert_number_of_calls(request, len(statuses))

    assert [record.record.data["id"] for record in output.records] == expected_ids
    assert [wait for wait in backoff_waits if wait] == expected_waits
    if expected_ids:
        assert not output.errors
    else:
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.transient_error
        assert error.internal_message.endswith("Last exception: Rate limits hit")
