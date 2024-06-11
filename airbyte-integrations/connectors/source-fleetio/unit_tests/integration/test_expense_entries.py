# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import SyncMode
from integration.config import ConfigBuilder
from source_fleetio import SourceFleetio

_AN_ACCOUNT_TOKEN = "example_account_token"  # used from our dev docs as an example
_AN_API_KEY = "example_api_key"  # used from our dev docs as an example
_STREAM_NAME = "expense_entries"
_TEMPLATE_NAME = "expense_entries"
_RECORDS_PATH = FieldPath("expense_entries")
_API_URL = "https://secure.fleetio.com/api"
_API_VERSION = "2024-03-15"


def _an_expense_entry() -> RecordBuilder:
    return create_record_builder(
        find_template(_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
    )


def _expense_entries_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
    )


def _read(
    config_builder: ConfigBuilder,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read(
        SourceFleetio(),
        config_builder.build(),
        CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        state,
        expecting_exception,
    )


class ExpenseEntriesTest(TestCase):
    @HttpMocker()
    def test_request_is_created_properly(self, http_mocker: HttpMocker):
        http_mocker.get(
            HttpRequest(
                url=f"{_API_URL}/v1/expense_entries",
                query_params={
                    "per_page": "100",
                },
                headers={
                    "Authorization": f"Token {_AN_API_KEY}",
                    "Account-Token": _AN_ACCOUNT_TOKEN,
                    "X-Client-Name": "data_connector",
                    "X-Client-Platform": "fleetio_airbyte",
                    "X-Api-Version": _API_VERSION,
                },
            ),
            _expense_entries_response().build(),
        )

        _read(
            ConfigBuilder()
            .with_account_token(_AN_ACCOUNT_TOKEN)
            .with_api_key(_AN_API_KEY)
        )
