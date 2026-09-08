# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import Mock, patch

import pytest
import requests
from source_expensify.source import (
    CredentialsInvalidError,
    ExpensifyReports,
    PolicyNotFoundError,
    RateLimitExceededError,
    SourceExpensify,
    _post_job_description,
)

from airbyte_cdk.models import SyncMode


@pytest.fixture
def stream():
    return ExpensifyReports(
        name="reports",
        partner_user_id="user-id",
        partner_user_secret="user-secret",
        start_date="2026-08-30",
        end_date="2026-08-31",
    )


class TestReadRecords:
    def test_read_records_yields_parsed_csv_rows(self, stream):
        csv_data = "reportID,amount\n1,100\n2,200\n"

        with (
            patch.object(stream, "_trigger_export", return_value="report.csv") as mock_trigger,
            patch.object(stream, "_download_file", return_value=csv_data) as mock_download,
        ):
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

        mock_trigger.assert_called_once_with()
        mock_download.assert_called_once_with("report.csv")

        assert records == [
            {"reportID": "1", "amount": "100"},
            {"reportID": "2", "amount": "200"},
        ]

    def test_read_records_no_rows(self, stream):
        csv_data = "reportID,amount\n"

        with (
            patch.object(stream, "_trigger_export", return_value="empty.csv"),
            patch.object(stream, "_download_file", return_value=csv_data),
        ):
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

        assert records == []

    def test_read_records_calls_steps_in_order(self, stream):
        call_order = []

        def trigger_export():
            call_order.append("trigger")
            return "file.csv"

        def download_file(file_name):
            call_order.append("download")
            assert file_name == "file.csv"
            return "reportID,amount\n1,50\n"

        with (
            patch.object(stream, "_trigger_export", side_effect=trigger_export),
            patch.object(stream, "_download_file", side_effect=download_file),
        ):
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

        assert call_order == ["trigger", "download"]
        assert records == [{"reportID": "1", "amount": "50"}]

    def test_read_records_propagates_trigger_export_error(self, stream):
        with (
            patch.object(stream, "_trigger_export", side_effect=requests.exceptions.HTTPError("boom")),
            patch.object(stream, "_download_file") as mock_download,
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                list(stream.read_records(sync_mode=SyncMode.full_refresh))

        mock_download.assert_not_called()

    def test_read_records_propagates_download_file_error(self, stream):
        with (
            patch.object(stream, "_trigger_export", return_value="file.csv"),
            patch.object(stream, "_download_file", side_effect=requests.exceptions.HTTPError("download failed")),
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                list(stream.read_records(sync_mode=SyncMode.full_refresh))


class TestTriggerExport:
    def test_trigger_export_uses_configured_date_range(self, stream):
        with patch("source_expensify.source._post_job_description") as mock_post:
            mock_post.return_value.text = "file.csv"

            stream._trigger_export()

        job_description = mock_post.call_args.args[0]
        assert job_description["inputSettings"]["filters"] == {
            "startDate": "2026-08-30",
            "endDate": "2026-08-31",
        }


class TestPostJobDescription:
    def test_posts_json_payload_and_returns_successful_response(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b"file.csv"

        with patch("source_expensify.source.requests.post", return_value=response) as mock_post:
            result = _post_job_description({"type": "download"})

        assert result is response
        mock_post.assert_called_once_with(
            "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations",
            data={"requestJobDescription": '{"type": "download"}'},
            timeout=60,
        )

    @pytest.mark.parametrize(
        ("response_code", "exception"),
        [
            (401, CredentialsInvalidError),
            (410, PolicyNotFoundError),
            (429, RateLimitExceededError),
        ],
    )
    def test_raises_for_expensify_error_response_codes(self, response_code, exception):
        response = requests.Response()
        response.status_code = 200
        response._content = f'{{"responseCode": {response_code}}}'.encode()

        with patch("source_expensify.source.requests.post", return_value=response):
            with pytest.raises(exception):
                _post_job_description({"type": "get"})

    def test_raises_for_http_server_errors(self):
        response = requests.Response()
        response.status_code = 503
        response.url = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"

        with patch("source_expensify.source.requests.post", return_value=response):
            with pytest.raises(requests.exceptions.HTTPError):
                _post_job_description({"type": "get"})


class TestDownloadFile:
    def test_download_file_posts_credentials_and_file_name(self, stream):
        response = requests.Response()
        response.status_code = 200
        response._content = b"reportID,amount\n1,100\n"

        with patch("source_expensify.source.requests.post", return_value=response) as mock_post:
            result = stream._download_file("report.csv")

        assert result == "reportID,amount\n1,100\n"
        job_description = json.loads(mock_post.call_args.kwargs["data"]["requestJobDescription"])
        assert job_description == {
            "type": "download",
            "credentials": {"partnerUserID": "user-id", "partnerUserSecret": "user-secret"},
            "fileName": "report.csv",
            "fileSystem": "integrationServer",
        }


class TestCheckConnection:
    def test_check_connection_accepts_valid_credentials(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"responseCode": 200}'
        source = SourceExpensify()
        logger = Mock()

        with patch("source_expensify.source.requests.post", return_value=response):
            result = source.check_connection(logger, {"partner_user_id": "user-id", "partner_user_secret": "user-secret"})

        assert result == (True, None)

    @pytest.mark.parametrize(
        ("response_code", "expected"),
        [
            (401, (False, None)),
            (410, (True, None)),
            (429, (False, RateLimitExceededError)),
        ],
    )
    def test_check_connection_classifies_expensify_errors(self, response_code, expected):
        response = requests.Response()
        response.status_code = 200
        response._content = f'{{"responseCode": {response_code}}}'.encode()
        source = SourceExpensify()
        logger = Mock()

        with patch("source_expensify.source.requests.post", return_value=response):
            result = source.check_connection(logger, {"partner_user_id": "user-id", "partner_user_secret": "user-secret"})

        assert result[0] is expected[0]
        if expected[1] is None:
            assert result[1] is None
        else:
            assert isinstance(result[1], expected[1])
