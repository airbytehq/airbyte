# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from typing import Any, Dict, Optional, Tuple
from unittest.mock import MagicMock, patch

from base_test import BaseTest
from source_bing_ads.source import SourceBingAds
from suds.transport.https import HttpAuthenticated
from suds_response_mock import mock_http_authenticated_send

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker


class TestAccountsStream(BaseTest):
    stream_name = "accounts"

    def read_stream(
        self,
        stream_name: str,
        sync_mode: SyncMode,
        config: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
        expecting_exception: bool = False,
    ) -> Tuple[EntrypointOutput, MagicMock]:
        with patch.object(HttpAuthenticated, "send", mock_http_authenticated_send):
            catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
            return read(SourceBingAds(), config, catalog, state, expecting_exception)

    @HttpMocker()
    def test_read_accounts_tax_certificate_data(self, http_mocker):
        # Our account doesn't have configured Tax certificate.
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config)
        assert output.records[0].record.data["TaxCertificate"] == {
            "Status": "Active",
            "TaxCertificateBlobContainerName": "Test Container Name",
            "TaxCertificates": [{"key": "test_key", "value": "test_value"}],
        }
