# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, Optional
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import SyncMode
from config import ConfigBuilder
from source_harvest import SourceHarvest

_A_START_DATE = "2021-01-01T00:00:00+00:00"
_AN_ACCOUNT_ID = "1209384"
_AN_API_KEY = "harvestapikey"
_STREAM_NAME = "invoices"
_TEMPLATE_NAME = "invoices"
_RECORDS_PATH = FieldPath("invoices")


def _an_invoice() -> RecordBuilder:
    return create_record_builder(
        find_template(_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
    )


def _invoices_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
    )


def _read(
    config_builder: ConfigBuilder,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    return read(
        SourceHarvest(),
        config_builder.build(),
        CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
        state,
        expecting_exception
    )


class InvoicesTest(TestCase):
    @HttpMocker()
    def test_given_start_date_when_read_then_request_is_created_properly(self, http_mocker: HttpMocker):

        datetime_start_date = datetime.fromisoformat(_A_START_DATE)
        string_formatted_start_date = datetime_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        http_mocker.get(
            HttpRequest(
                url="https://api.harvestapp.com/v2/invoices",
                query_params={
                    "per_page": "50",
                    "updated_since": string_formatted_start_date,
                },
                headers={
                    "Authorization": f"Bearer {_AN_API_KEY}",
                    "Harvest-Account-ID": _AN_ACCOUNT_ID,
                }
            ),
            _invoices_response().build()
        )

        _read(ConfigBuilder().with_account_id(_AN_ACCOUNT_ID).with_api_token(_AN_API_KEY).with_replication_start_date(datetime_start_date))

        # endpoint is called
