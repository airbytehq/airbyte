# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
from pathlib import Path
from typing import Optional

from base_test import BaseTest
from bingads.v13.bulk.bulk_service_manager import BulkServiceManager
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from request_builder import RequestBuilder
from airbyte_cdk.test.mock_http.response_builder import find_template

class TestBulkStream(BaseTest):
    @property
    def service_manager(self) -> BulkServiceManager:
        return BulkServiceManager

    def mock_bulk_download_request(self):
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk").with_body(
                '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["AppInstallAdLabels"], "DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
            ).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
    
    def mock_bulk_download_status_query(self):
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body(
                '{"RequestId": "TestDownloadRequestId"}'
            ).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
        )

    def mock_download(self, file: str):
        http_mocker = self.http_mocker
        path_to_file_base = Path(__file__).parent.parent / f"resource/response/{file}.csv"
        with open(path_to_file_base, "r") as file:
            file_content = file.read()
        encoded_file_content = file_content.encode("utf-8-sig")
        http_mocker.get(
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
            HttpResponse(encoded_file_content, 200),
        )

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
