# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for the per-currency `calendar` and `data_catalogue` streams."""

from typing import Any, Dict
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import FXMacroDataRequestBuilder, json_response


def _read(stream_name: str, config: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog)


class TestCalendarStream(TestCase):
    @HttpMocker()
    def test_reads_rows_for_each_currency(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_key("test-api-key").with_currencies("USD", "GBP").build()
        for currency, release in (("USD", "non_farm_payrolls"), ("GBP", "inflation")):
            http_mocker.get(
                FXMacroDataRequestBuilder.calendar_endpoint(currency).build(),
                json_response(
                    {
                        "currency": currency,
                        "data": [
                            {
                                "announcement_datetime": 1791030600,
                                "release": release,
                                "calendar_event_id": f"{currency.lower()}_{release}_1791030600",
                            }
                        ],
                    }
                ),
            )

        output = _read("calendar", config)

        assert sorted((r.record.data["currency"], r.record.data["release"]) for r in output.records) == [
            ("GBP", "inflation"),
            ("USD", "non_farm_payrolls"),
        ]


class TestDataCatalogueStream(TestCase):
    @HttpMocker()
    def test_one_record_per_indicator(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            FXMacroDataRequestBuilder.data_catalogue_endpoint("USD").build(),
            json_response(
                {
                    "gdp": {"name": "GDP", "unit": "USD bn", "frequency": "Quarterly"},
                    "policy_rate": {"name": "Federal Funds Target Rate", "unit": "%", "frequency": "Irregular"},
                }
            ),
        )

        output = _read("data_catalogue", ConfigBuilder().build())

        records = sorted((r.record.data for r in output.records), key=lambda r: r["indicator"])
        assert [(r["currency"], r["indicator"], r["name"]) for r in records] == [
            ("USD", "gdp", "GDP"),
            ("USD", "policy_rate", "Federal Funds Target Rate"),
        ]
        assert records[0]["frequency"] == "Quarterly"
