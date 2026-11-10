# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import request_for
from .response_builder import response_for


@pytest.mark.parametrize("api_key", ["first-test-key", "second-test-key"])
@pytest.mark.parametrize("status_code", [200, 401])
def test_check(http_mocker: HttpMocker, api_key: str, status_code: int) -> None:
    config = ConfigBuilder().with_api_key(api_key).with_query("activities", "hiking").build()
    request = request_for("activities", config)
    response = (
        response_for("activities", "ActivityID", [7]) if status_code == 200 else HttpResponse('{"message": "Invalid API key"}', status_code)
    )
    http_mocker.get(request, response)

    result = get_source(config).check(logging.getLogger("test"), config)

    assert result.status == (Status.SUCCEEDED if status_code == 200 else Status.FAILED)
    if status_code == 401:
        assert result.message.replace("HTTP Status Code: 401. Error: ", "") == repr(
            "Stream activities is not available: Unauthorized. Please ensure you are authenticated correctly."
        )
    http_mocker.assert_number_of_calls(request, 1)


def test_read_auth_error(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().with_query("activities", "hiking").build()
    request = request_for("activities", config)
    http_mocker.get(request, HttpResponse('{"message": "Invalid API key"}', 401))
    catalog = CatalogBuilder().with_stream("activities", SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog, expecting_exception=True)

    assert output.records == []
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert error.message.removeprefix("HTTP Status Code: 401. Error: ") == "Unauthorized. Please ensure you are authenticated correctly."
    http_mocker.assert_number_of_calls(request, 1)
