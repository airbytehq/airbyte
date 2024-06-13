# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from freezegun import freeze_time
from test_bulk_stream import TestBulkStream


class TestAppInstallAdsStream(TestBulkStream):
    stream_name = "app_install_ads"
    account_id = "180535609"
    cursor_field = "Modified Time"

    @HttpMocker()
    def test_return_records_from_given_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads")
        assert len(output.records) == 1

    @HttpMocker()
    def test_return_logged_info_for_empty_csv_file(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads_empty")
        assert len(output.records) == 0
        assert len(output.logs) == 10

    @HttpMocker()
    def test_transform_records(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads")
        assert output.records
        for record in output.records:
            assert "Account Id" in record.record.data.keys()
            assert isinstance(record.record.data["Account Id"], int)

    @HttpMocker()
    def test_incremental_read_cursor_value_matches_value_from_most_recent_record(self, http_mocker: HttpMocker):
        self.auth_client(http_mocker)
        output, _ = self.read_stream(self.stream_name, SyncMode.incremental, self._config, "app_install_ads_with_cursor_value")
        assert len(output.records) == 4
        assert dict(output.most_recent_state.stream_state).get(self.account_id, {}) == {self.cursor_field: "2024-03-01T12:49:12.028+00:00"}

    @HttpMocker()
    @freeze_time("2023-12-29")  # mock current time as stream data available for 30 days only
    def test_incremental_read_with_state(self, http_mocker: HttpMocker):
        state = self._state("app_install_ads_state", self.stream_name)
        self.auth_client(http_mocker)
        output, service_call_mock = self.read_stream(self.stream_name, SyncMode.incremental, self._config, "app_install_ads_with_state", state)
        assert dict(output.most_recent_state.stream_state).get(self.account_id, {}) == {self.cursor_field: "2024-01-01T10:55:12.028+00:00"}

        previous_state = state[0].stream.stream_state.dict()
        # gets DownloadParams object
        assert service_call_mock.call_args.args[0].last_sync_time_in_utc == pendulum.parse(previous_state[self.account_id][self.cursor_field])
