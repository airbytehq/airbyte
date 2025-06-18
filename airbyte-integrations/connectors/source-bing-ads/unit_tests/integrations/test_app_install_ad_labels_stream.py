# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json

import pendulum
from freezegun import freeze_time
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpResponse
from request_builder import RequestBuilder
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestAppInstallAdLabelsStream(TestBulkStream):
    stream_name = "app_install_ad_labels"
    account_id = "180535609"
    cursor_field = "Modified Time"

    def mock_apis(self, file: str):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.mock_download(file=file)

    def test_return_records_from_given_csv_file(self):
        self.mock_apis(file=self.stream_name)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ad_labels")
        assert len(output.records) == 1

    def test_return_logged_info_for_empty_csv_file(self):
        self.mock_apis(file="app_install_ad_labels_empty")
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ad_labels_empty")
        assert len(output.records) == 0
        no_records_message = self.create_log_message(f"Read 0 records from {self.stream_name} stream")
        assert no_records_message in output.logs

    def test_transform_records(self):
        self.mock_apis(file=self.stream_name)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ad_labels")
        assert output.records
        for record in output.records:
            assert "Account Id" in record.record.data.keys()
            assert isinstance(record.record.data["Account Id"], int)

    @freeze_time("2024-02-26")
    def test_incremental_read_cursor_value_matches_value_from_most_recent_record(self):
        self.mock_apis(file="app_install_ad_labels_with_cursor_value")
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, "app_install_ad_labels_with_cursor_value")
        assert len(output.records) == 4
        assert output.most_recent_state.stream_state.states[0]["cursor"] == {
            self.cursor_field: "2024-01-04T12:12:12.028+0000"
        }

    @freeze_time("2024-02-26")  # mock current time as stream data available for 30 days only
    def test_incremental_read_with_state(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk").with_body(
                '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["AppInstallAdLabels"], "DownloadFileType": "Csv", "FormatVersion": "6.0", "LastSyncTimeInUTC": "2024-01-29T12:54:12.028+00:00", "CompressionType": "GZip"}'
            ).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
        self.mock_bulk_download_status_query()
        self.mock_download(file="app_install_ad_labels_with_state")
        state = self._state("app_install_ad_labels_state", self.stream_name)
        output, service_call_mock = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, "app_install_ad_labels_with_state", state
        )
        assert output.most_recent_state.stream_state.states[0]["cursor"] == {
            self.cursor_field: "2024-01-29T12:55:12.028+0000"
        }
