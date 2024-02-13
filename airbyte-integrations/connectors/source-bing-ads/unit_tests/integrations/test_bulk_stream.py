from pathlib import Path
from typing import Dict, Any, Optional
from unittest import TestCase
from unittest.mock import patch

import suds.transport
from airbyte_cdk.models import SyncMode

from source_bing_ads.client import Client
from config import ConfigBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from source_bing_ads.source import SourceBingAds

from client_builder import build_request, response_with_status
from source_bing_ads.base_streams import BingAdsStream
from suds.transport.https import HttpAuthenticated
from bingads.v13.bulk.bulk_service_manager import BulkServiceManager
from constants import AD_ACC_DATA
from catalog_builder import CatalogBuilder


class TestBulkStream(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _state(self, file: str) -> Path:
        Path(__file__).parent.parent / f"resource/state/{file}.json"

    def _download_file(self, file: str = None) -> Path:
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

        with patch.object(BingAdsStream, "_get_user_id", return_value=11111111):
            with patch.object(HttpAuthenticated, "send", return_value=suds.transport.Reply(code=200, headers={}, message=AD_ACC_DATA)):
                with patch.object(BulkServiceManager, "download_file", return_value=self._download_file(stream_data_file)):

                    catalog = CatalogBuilder().with_stream(stream_name, sync_mode, pk).build()
                    return read(SourceBingAds(), config, catalog, state, expecting_exception)

