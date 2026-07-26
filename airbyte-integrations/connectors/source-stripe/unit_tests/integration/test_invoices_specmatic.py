# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from integration.config import ConfigBuilder


_STREAM_NAME = "invoices"
_NOW_IMPORT = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}

_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}


def get_dates():
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=60)
    return now, start_date


def _config(now) -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(now - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _read(config_builder: ConfigBuilder, sync_mode: SyncMode, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    config["url_base"] = _CONFIG["url_base"]
    return read(get_source(config, _NO_STATE), config, catalog, _NO_STATE, expecting_exception)


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class InvoicesSpecmaticFullRefreshTest(SpecmaticIntegrationTestCase):
    """
    Specmatic-backed integration tests for GET /v1/invoices.
    These tests exercise the endpoint defined in stripe-official.json through
    the Specmatic mock server, contributing to Mock Usage Report coverage.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    def test_given_one_page_when_read_then_return_records(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/invoices",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "expand[]": "data.discounts",
            },
            response_body={
                "object": "list",
                "url": "/v1/invoices",
                "has_more": False,
                "data": [
                    {"id": "in_1", "object": "invoice", "created": int(start_date.timestamp())},
                    {"id": "in_2", "object": "invoice", "created": int(start_date.timestamp())},
                ],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 2

    def test_given_many_pages_when_read_then_return_all_records(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/invoices",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "expand[]": "data.discounts",
            },
            response_body={
                "object": "list",
                "url": "/v1/invoices",
                "has_more": True,
                "data": [{"id": "last_record_id_from_first_page", "object": "invoice", "created": int(start_date.timestamp())}],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/invoices",
            query={
                "starting_after": "last_record_id_from_first_page",
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "expand[]": "data.discounts",
            },
            response_body={
                "object": "list",
                "url": "/v1/invoices",
                "has_more": False,
                "data": [
                    {"id": "in_1", "object": "invoice", "created": int(start_date.timestamp())},
                    {"id": "in_2", "object": "invoice", "created": int(start_date.timestamp())},
                ],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 3

    def test_given_empty_response_when_read_then_return_no_records(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/invoices",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "expand[]": "data.discounts",
            },
            response_body={"object": "list", "url": "/v1/invoices", "has_more": False, "data": []},
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 0
