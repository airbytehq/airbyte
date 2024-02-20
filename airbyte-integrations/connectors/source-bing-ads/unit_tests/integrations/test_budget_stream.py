# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from test_bulk_stream import TestBulkStream


class TestBudgetStream(TestBulkStream):
    stream_name = "budget"
    account_id = "180535609"

    @HttpMocker()
    def test_return_records_from_given_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, [], "budget")
        assert len(output.records) == 1

    @HttpMocker()
    def test_return_logged_info_for_empty_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, [], "budget_empty")
        assert len(output.records) == 0
        assert "Empty data received. No columns to parse from file" in [log.log.message for log in output.logs]

    @HttpMocker()
    def test_return_logged_fatal_for_ioerror(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, [], stream_data_file=None)
        fatal_log = [log.log for log in output.logs if log.log.level == Level.FATAL]
        assert fatal_log
        assert "The IO/Error occurred while reading tmp data. Called:" in fatal_log[0].message
        assert len(output.records) == 0

    @HttpMocker()
    def test_transform_records(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, [], "budget")
        for record in output.records:
            assert "Account Id" in record.record.data.keys()
            assert isinstance(record.record.data["Account Id"], int)

    @HttpMocker()
    def test_reads_with_chunks_from_given_csv_file_with_big_amount_of_data(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, [], "budget_big_data")
        assert len(output.records) == 3289

    @HttpMocker()
    def test_incremental_read_cursor_value_matches_value_from_most_recent_record(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, [], "budget_with_cursor_value")
        assert len(output.records) == 8
        assert output.most_recent_state.get(self.stream_name, {}).get(self.account_id, {}) == {"Modified Time": "2024-01-01T12:54:12.028+00:00"}

    @HttpMocker()
    def test_incremental_read_with_state(self, http_mocker: HttpMocker):
        state = self._state("budget_state")
        self.auth_client(http_mocker)
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, [], "budget_with_state", state)
        assert len(output.records) == 8
        assert output.most_recent_state.get(self.stream_name, {}).get(self.account_id, {}) == {"Modified Time": "2024-01-02T12:54:12.028+00:00"}
