# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server coverage for `tracking_categories` on `costcentres` and `products`.

Uptick returns the field as an array of objects (or `[]`), and 3.0.0 declares it that way. These
tests read each stream with both shapes and assert the value is emitted unchanged, so a future
schema or transformation edit cannot silently drop or reshape it.
"""

import json
from typing import Any

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_TOKEN_REQUEST = HttpRequest(
    url=UptickRequestBuilder.token_endpoint(),
    body="grant_type=password&client_id=test-client-id&client_secret=test-client-secret&username=test-user&password=test-password",
)
_TOKEN_RESPONSE = HttpResponse(body=json.dumps({"access_token": "tok", "expires_in": 3600}), status_code=200)
_MODELS = {"costcentres": "CostCentre", "products": "Product"}
_TRACKING_CATEGORIES = [
    pytest.param([], id="empty_array"),
    pytest.param(
        [{"id": 1, "name": "Region", "option": "North"}, {"id": 2, "name": "Department", "option": "Service"}],
        id="array_of_objects",
    ),
]


def _record(stream: str, tracking_categories: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "type": _MODELS[stream],
        "id": 1,
        "attributes": {
            "created": "2026-01-01T00:00:00.000000+0000",
            "updated": "2026-01-02T00:00:00.000000+0000",
            "name": "Record",
            "tracking_categories": tracking_categories,
        },
        "relationships": {},
    }


@pytest.mark.parametrize("stream", sorted(_MODELS))
@pytest.mark.parametrize("tracking_categories", _TRACKING_CATEGORIES)
def test_tracking_categories_array_is_emitted_unchanged(stream: str, tracking_categories: list[dict[str, Any]]) -> None:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection(stream)

    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        http_mocker.get(
            page_request,
            HttpResponse(body=json.dumps({"data": [_record(stream, tracking_categories)], "links": {"next": None}}), status_code=200),
        )

        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        http_mocker.assert_number_of_calls(page_request, 1)

    assert output.errors == []
    assert [message.record.data["tracking_categories"] for message in output.records] == [tracking_categories]
    assert not [log for log in output.logs if "does not conform to schema" in log.log.message]
    assert output.get_stream_statuses(stream)[-1].name == "COMPLETE"
