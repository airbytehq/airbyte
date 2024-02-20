# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from bingads.v13.bulk import BulkServiceManager
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from catalog_builder import BingAdsCatalogBuilder
from client_builder import build_request, response_with_status
from config_builder import ConfigBuilder
from source_bing_ads.source import SourceBingAds
from suds.transport.https import HttpAuthenticated
from suds_response_mock import mock_http_authenticated_send


class BaseTest(TestCase):

    @property
    def service_manager(self) -> ReportingServiceManager | BulkServiceManager:
        pass

    def _download_file(self, file: Optional[str] = None) -> Path:
        pass

    @property
    def _config(self) -> dict[str, Any]:
        return ConfigBuilder().build()

    def _state(self, file: str) -> Path:
        Path(__file__).parent.parent / f"resource/state/{file}.json"

    def auth_client(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            request=build_request(self._config),
            responses=response_with_status("oauth", 200)
        )

    def read_stream(
            self, stream_name: str,
            sync_mode: SyncMode,
            config: Dict[str, Any],
            pk: list[str],
            stream_data_file: str = None,
            state: Optional[Dict[str, Any]] = None,
            expecting_exception: bool = False,
    ) -> EntrypointOutput:
        with patch.object(HttpAuthenticated, "send", mock_http_authenticated_send):
            with patch.object(self.service_manager, "download_file", return_value=self._download_file(stream_data_file)):
                catalog = BingAdsCatalogBuilder().with_stream(stream_name, sync_mode, pk).build()
                return read(SourceBingAds(), config, catalog, state, expecting_exception)
