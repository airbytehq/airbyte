# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from bingads.v13.bulk.bulk_service_manager import BulkServiceManager
from catalog_builder import BingAdsCatalogBuilder
from client_builder import build_request, response_with_status
from config import ConfigBuilder
from source_bing_ads.client import Client
from source_bing_ads.source import SourceBingAds
from suds.transport.https import HttpAuthenticated
from suds_response_mock import mock_http_authenticated_send


class TestBulkStream(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _state(self, file: str) -> Path:
        Path(__file__).parent.parent / f"resource/state/{file}.json"

    def _download_file(self, file: Optional[str] = None) -> Path:
        """
        Returns path to temporary file of downloaded data that will be use in read.
        Base file should be named as {file_name}.cvs in resource/response folder.
        """
        if file:
            path_to_tmp_file = Path(__file__).parent.parent / f"resource/response/{file}_tmp.csv"
            path_to_file_base = Path(__file__).parent.parent / f"resource/response/{file}.csv"
            with open(path_to_file_base, "r") as f1, open(path_to_tmp_file, "w") as f2:
                for line in f1:
                    f2.write(line)
            return path_to_tmp_file
        return Path(__file__).parent.parent / "resource/response/non-existing-file.csv"

    def _get_client(self, http_mocker, config: dict) -> Client:
        http_mocker.post(
            request=build_request(self._config),
            responses=response_with_status("oauth", 200)
        )
        client = Client(**config)
        return client

    def read_stream(
            self, stream_name: str, sync_mode: SyncMode, config: Dict[str, Any], pk: list[str], stream_data_file: str,
            state: Optional[Dict[str, Any]] = None,expecting_exception: bool = False,
    ) -> EntrypointOutput:
        with patch.object(HttpAuthenticated, "send", mock_http_authenticated_send):
            with patch.object(BulkServiceManager, "download_file", return_value=self._download_file(stream_data_file)):

                catalog = BingAdsCatalogBuilder().with_stream(stream_name, sync_mode, pk).build()
                return read(SourceBingAds(), config, catalog, state, expecting_exception)
