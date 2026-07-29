#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "payment_intents"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"


def _payment_intents_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.payment_intents_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _a_payment_intent() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _payment_intents_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_STREAM_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _payment_intents_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _payment_intents_response().with_record(_a_payment_intent()).with_record(_a_payment_intent()).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE), SyncMode.full_refresh)

        assert len(output.records) == 2
