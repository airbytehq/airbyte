# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""`customers` cursor contract for RevenueCat's default anonymous app user IDs."""

import pytest

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder, next_page_path
from mock_server.streams import PROJECT_ID, list_response, mock_ancestors, record


_STREAM = "customers"
_ANONYMOUS_ID = "$RCAnonymousID:abc"
_ANONYMOUS_ID_ENCODED = "%24RCAnonymousID%3Aabc"


@pytest.mark.parametrize(
    "next_page_extra",
    [pytest.param(None, id="cursor_only"), pytest.param("limit=100", id="next_page_carries_limit")],
)
def test_anonymous_id_cursor_is_sent_encoded_once_and_read_terminates(next_page_extra) -> None:
    path = f"/projects/{PROJECT_ID}/customers"
    with HttpMocker() as http_mocker:
        mock_ancestors(http_mocker, _STREAM, [PROJECT_ID])
        page_two = RevenueCatRequestBuilder.endpoint(path).with_starting_after(_ANONYMOUS_ID).build()
        http_mocker.get(
            RevenueCatRequestBuilder.endpoint(path).build(),
            list_response(
                _STREAM,
                [record(_STREAM, "app_user_1"), record(_STREAM, _ANONYMOUS_ID)],
                next_page=next_page_path(path, _ANONYMOUS_ID_ENCODED, next_page_extra),
            ),
        )
        http_mocker.get(page_two, list_response(_STREAM, [record(_STREAM, "app_user_2")], next_page=None))

        output = read_stream(_STREAM)

    assert output.errors == []
    assert [r["id"] for r in records_data(output)] == ["app_user_1", _ANONYMOUS_ID, "app_user_2"]
    http_mocker.assert_number_of_calls(page_two, 1)
