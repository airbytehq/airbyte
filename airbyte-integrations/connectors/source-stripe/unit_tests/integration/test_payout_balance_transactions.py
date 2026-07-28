#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder


_STREAM_NAME = "payout_balance_transactions"
_A_PAYOUT_ID = "a_payout_id"
_ANOTHER_PAYOUT_ID = "another_payout_id"
_NOW_IMPORT = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)

_EVENT_TYPES = [
    "payout.canceled",
    "payout.created",
    "payout.failed",
    "payout.paid",
    "payout.reconciliation_completed",
    "payout.updated",
]

_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}


def get_dates():
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=75)
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


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    config["url_base"] = _CONFIG["url_base"]
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class PayoutBalanceTransactionsFullRefreshTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    def test_given_multiple_parents_when_read_then_extract_from_all_children(self) -> None:
        """Zero-Hardcoding contract read for payout balance transactions."""
        now, start_date = get_dates()
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 2


    def test_when_read_then_add_payout_field(self) -> None:
        now, start_date = get_dates()

        self.set_specmatic_expectation(
            path="/v1/payouts",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/payouts",
                "has_more": False,
                "data": [{"id": _A_PAYOUT_ID, "object": "payout", "created": int(start_date.timestamp())}],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/balance_transactions",
            query={"payout": _A_PAYOUT_ID, "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/balance_transactions",
                "has_more": False,
                "data": [{"id": "txn_1", "object": "balance_transaction", "created": int(start_date.timestamp())}],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert output.records[0].record.data["payout"]


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class PayoutBalanceTransactionsIncrementalTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(
        self, config: ConfigBuilder, state: Optional[List[AirbyteStateMessage]], expecting_exception: bool = False
    ) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)

    def test_when_read_then_fetch_from_updated_payouts(self) -> None:
        now, start_date = get_dates()
        state_date = now - timedelta(days=10)

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_date.timestamp())),
                "created[lte]": str(int(now.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(state_date.timestamp()),
                        "data": {
                            "object": {
                                "id": _A_PAYOUT_ID,
                                "object": "payout",
                                "created": int(state_date.timestamp()),
                                "updated": int(state_date.timestamp()),
                            }
                        },
                    }
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/balance_transactions",
            query={"payout": _A_PAYOUT_ID, "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/balance_transactions",
                "has_more": False,
                "data": [{"id": "txn_1", "object": "balance_transaction", "created": int(state_date.timestamp())}],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_date.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        output = self._read(_config(now).with_start_date(start_date), state)
        assert len(output.records) == 1
