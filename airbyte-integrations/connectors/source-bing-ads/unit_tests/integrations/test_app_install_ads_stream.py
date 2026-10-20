# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import gzip
from pathlib import Path

from freezegun import freeze_time
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpResponse


class TestAppInstallAdsStream(TestBulkStream):
    stream_name = "app_install_ads"
    account_id = "180535609"
    cursor_field = "Modified Time"
    download_entity = "AppInstallAds"

    def test_return_records_from_given_csv_file(self):
        self.mock_apis(file=self.stream_name)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads")
        assert len(output.records) == 1

    def test_return_zero_record_from_empty_csv(self):
        self.mock_apis(file="app_install_ads_empty")
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads_empty")
        assert len(output.records) == 0
        no_records_message = self.create_log_message(f"Read 0 records from {self.stream_name} stream")
        assert no_records_message in output.logs

    def test_transform_records(self):
        self.mock_apis(file=self.stream_name)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads")
        assert output.records
        for record in output.records:
            assert "Account Id" in record.record.data.keys()
            assert isinstance(record.record.data["Account Id"], int)

    @freeze_time("2024-02-26")
    def test_incremental_read_cursor_value_matches_value_from_most_recent_record(self):
        self.mock_apis(file="app_install_ads_with_cursor_value")
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, "app_install_ads_with_cursor_value")
        assert len(output.records) == 4
        assert output.most_recent_state.stream_state.states[0]["cursor"] == {self.cursor_field: "2024-03-01T12:49:12.028+0000"}

    @freeze_time("2024-02-26")
    def test_incremental_read_interrupted_download_does_not_advance_cursor(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        # Without its gzip trailer the file still decompresses row by row, then ends before the
        # end-of-stream marker, as it does when the connection drops before the whole file arrives.
        csv_path = Path(__file__).parent.parent / "resource/response/app_install_ads_with_cursor_value.csv"
        truncated_file = gzip.compress(csv_path.read_text().encode("utf-8-sig"))[:-8]
        self.http_mocker.get(
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
            HttpResponse(truncated_file, 200),
        )

        output = self.read_stream(
            self.stream_name, SyncMode.incremental, self._config, "app_install_ads_with_cursor_value", expecting_exception=True
        )

        # Rows read before the cut-off are emitted and the stream fails, but the cursor stays at the
        # default start date (one year back) instead of moving past records that never arrived.
        assert output.records
        assert output.errors
        assert output.most_recent_state.stream_state.states[0]["cursor"] == {self.cursor_field: "2023-02-26T00:00:00.000+0000"}

    @freeze_time("2024-02-26")  # mock current time as stream data available for 30 days only
    def test_incremental_read_with_state(self):
        self.mock_apis(file="app_install_ads_with_state", read_with_state=True)
        state = self._state("app_install_ads_state", self.stream_name)
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, "app_install_ads_with_state", state)
        assert output.most_recent_state.stream_state.states[0]["cursor"] == {self.cursor_field: "2024-01-29T12:55:12.028+0000"}
