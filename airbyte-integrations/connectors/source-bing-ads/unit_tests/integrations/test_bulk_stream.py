# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
from pathlib import Path
from typing import Optional

from base_test import BaseTest
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


EXPIRED_SAS_RESPONSE_BODY = (
    "<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [2024-01-01T00:00:00Z] "
    "- Expiry [2024-01-01T00:10:00Z] - Current [2024-01-01T00:11:00Z]</AuthenticationErrorDetail></Error>"
)
PERMISSION_MISMATCH_RESPONSE_BODY = (
    "<Error><Code>AuthorizationPermissionMismatch</Code><Message>This request is not authorized to perform this "
    "operation using this permission.</Message></Error>"
)
EXPIRED_SAS_ERROR_MESSAGE = "Bing Ads file download URL is expired."
DEFAULT_FORBIDDEN_ERROR_MESSAGE = "Forbidden. You don't have permission to access this resource."


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


class TestBulkDownloadErrorHandling(TestBulkStream):
    stream_name = "budget"
    download_entity = "Budgets"

    def mock_apis_with_download_response(self, response: HttpResponse):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.http_mocker.get(
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
            response,
        )

    def _read_with_download_response(self, response: HttpResponse):
        self.mock_apis_with_download_response(response)
        return self.read_stream(
            self.stream_name,
            SyncMode.full_refresh,
            self._config,
            stream_data_file="budget",
            expecting_exception=True,
        )

    def _assert_error(self, output, failure_type: str, message: str, message_contains: bool = False):
        errors = [message.trace.error for message in output.errors]
        assert any(
            getattr(error.failure_type, "value", error.failure_type) == failure_type
            and (message in error.message if message_contains else error.message == message)
            for error in errors
        ), [(error.failure_type, error.message) for error in errors]

    def test_expired_download_url_is_transient_error(self):
        output = self._read_with_download_response(
            HttpResponse(
                EXPIRED_SAS_RESPONSE_BODY,
                403,
                headers={"x-ms-error-code": "AuthenticationFailed"},
            )
        )

        self._assert_error(output, "transient_error", EXPIRED_SAS_ERROR_MESSAGE)

    def test_other_download_forbidden_error_remains_config_error(self):
        output = self._read_with_download_response(
            HttpResponse(
                PERMISSION_MISMATCH_RESPONSE_BODY,
                403,
                headers={"x-ms-error-code": "AuthorizationPermissionMismatch"},
            )
        )

        self._assert_error(output, "config_error", DEFAULT_FORBIDDEN_ERROR_MESSAGE, message_contains=True)
