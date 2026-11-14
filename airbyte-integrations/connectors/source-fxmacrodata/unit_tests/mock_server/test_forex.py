# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import FXMacroDataRequestBuilder, paged_response


_STREAM_NAME = "forex"
_START_DATE = "2026-09-01"


def _read(config: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config), config=config, catalog=catalog)


class TestForexStream(TestCase):
    @HttpMocker()
    def test_pairs_are_split_into_base_and_quote(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_key("test-api-key").with_forex_pairs("EUR/USD", "USDJPY").with_start_date(_START_DATE).build()
        for base, quote, val in (("EUR", "USD", 1.1712), ("USD", "JPY", 147.85)):
            http_mocker.get(
                FXMacroDataRequestBuilder.forex_endpoint(base, quote)
                .with_start_date(_START_DATE)
                .with_header("X-API-Key", "test-api-key")
                .build(),
                paged_response([{"date": "2026-09-30", "val": val}], base=base, quote=quote),
            )

        output = _read(config)

        records = sorted((r.record.data for r in output.records), key=lambda r: r["base"])
        assert [(r["base"], r["quote"], r["val"]) for r in records] == [("EUR", "USD", 1.1712), ("USD", "JPY", 147.85)]

    @HttpMocker()
    def test_pagination_follows_next_offset(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_key("test-api-key").with_forex_pairs("EUR/USD").with_start_date(_START_DATE).build()
        builder = FXMacroDataRequestBuilder.forex_endpoint("EUR", "USD").with_start_date(_START_DATE)
        http_mocker.get(builder.build(), paged_response([{"date": "2026-09-30", "val": 1.1712}], next_offset=100))
        http_mocker.get(builder.with_offset(100).build(), paged_response([{"date": "2026-09-29", "val": None}]))

        output = _read(config)

        assert [(r.record.data["date"], r.record.data.get("val")) for r in output.records] == [("2026-09-30", 1.1712), ("2026-09-29", None)]

    def test_no_pairs_configured_reads_nothing(self) -> None:
        # No HttpMocker routes are registered, so any request would fail the test.
        with HttpMocker():
            output = _read(ConfigBuilder().build())

        assert output.records == []
        assert output.errors == []
