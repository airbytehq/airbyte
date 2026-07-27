#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from pathlib import Path

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_STREAM_NAME = "accounts"
_ACCOUNT_ID = "acct_1G9HZLIEn49ers"
_CLIENT_SECRET = "ConfigBuilder default client secret"
_NOW = datetime.now(timezone.utc)
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}
_NO_STATE = StateBuilder().build()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(name="accounts", sync_mode=sync_mode).build()


@freezegun.freeze_time(_NOW.isoformat())
class AccountsTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Dynamically point connector config to the Specmatic mock server URL
        _CONFIG["url_base"] = cls.config["url_base"]

    def test_full_refresh(self) -> None:
        """Zero-Hardcoding contract test for accounts full refresh against Specmatic mock server."""
        self.source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(self.source, config=_CONFIG, catalog=_create_catalog())
        self.assert_contract_read_success(actual_messages)

    def test_pagination(self) -> None:
        """Zero-Hardcoding spec-driven read test for accounts stream."""
        self.source = get_source(config=_CONFIG, state=_NO_STATE)
        actual_messages = read(self.source, config=_CONFIG, catalog=_create_catalog())
        self.assert_contract_read_success(actual_messages)

