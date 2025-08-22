# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
from pathlib import Path
from typing import Optional

from base_test import BaseTest
from request_builder import RequestBuilder

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestBulkStream(BaseTest):
    download_entity: str = None

    def mock_apis(self, file: str, read_with_state: Optional[bool] = False):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request(read_with_state)
        self.mock_bulk_download_status_query()
        self.mock_download(file=file)

    def mock_bulk_download_request(self, read_with_state: Optional[bool] = False):
        http_mocker = self.http_mocker
        if not read_with_state:
            http_mocker.post(
                RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk")
                .with_body(
                    '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities":'
                    f' ["{self.download_entity}"], '
                    '"DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
                )
                .build(),
                HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
            )
        else:
            http_mocker.post(
                RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk")
                .with_body(
                    '{"AccountIds": ["180535609"], "DataScope": "EntityData", '
                    f'"DownloadEntities": ["{self.download_entity}"], '
                    '"DownloadFileType": "Csv", "FormatVersion": "6.0", "LastSyncTimeInUTC": "2024-01-29T12:54:12.028+00:00", "CompressionType": "GZip"}'
                )
                .build(),
                HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
            )

    def mock_bulk_download_status_query(self):
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk")
            .with_body('{"RequestId": "TestDownloadRequestId"}')
            .build(),
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
