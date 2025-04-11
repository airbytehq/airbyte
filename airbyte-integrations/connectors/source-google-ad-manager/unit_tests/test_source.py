from airbyte_protocol_dataclasses.models import SyncMode, Type, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, \
    StreamDescriptor, Status, AirbyteCatalog, AirbyteStream

from source_google_ad_manager.source import SourceGoogleAdManager
from datetime import datetime
import pandas as pd
import pytest


def DownloadReportToFile(report_job_id, report_download_format, temp_file, use_gzip_compression):
    input_str = open("./unit_tests/report_file.csv", encoding="utf-8").read()
    temp_file.write(input_str.encode("utf-8"))

class TestCheck:

    # Start date later than end date
    def test_start_date_greater_than_end_date(self, mocker):
        # Mock logger
        mock_logger = mocker.Mock()
    
        # Invalid config: start date after end date
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": '{"client_email": "fake@example.com", "token_uri": "https://oauth2.googleapis.com/token"}',
            "startDate": "2023-01-31",
            "endDate": "2023-01-01"
        }
    
        # Create instance and call check
        source = SourceGoogleAdManager()
        status = source.check(mock_logger, mock_config)
    
        # Assertions
        assert status.status == Status.FAILED
        assert status.message == "start_date (2023-01-31) cannot be greater than end_date (2023-01-01)."

    def test_check_successful_connection(self, mocker):
        # Mock dependencies
        mock_logger = mocker.Mock()
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": '{"client_email": "fake@example.com", "token_uri": "https://oauth2.googleapis.com/token"}',
            "startDate": "1972-12-17",
            "endDate": "1972-12-19"
        }
        mock_adManagerClient = mocker.Mock()
        mock_adManagerClient.create_ad_manager_client = mocker.Mock()
        mock_adManagerClient.create_ad_manager_client.return_value = mock_adManagerClient
        mocker.patch(
            'source_google_ad_manager.source.create_ad_manager_client', return_value=mock_adManagerClient)
        source = SourceGoogleAdManager()
        result = source.check(logger=mock_logger, config=mock_config)

        # Assert the result is a successful connection
        assert result.status == Status.SUCCEEDED

    def test_check_failed_connection(self, mocker):
        # Mock dependencies
        mock_logger = mocker.Mock()
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": '{"client_email": "fake@example.com", "token_uri": "https://oauth2.googleapis.com/token"}',
            "startDate": "1972-12-17",
            "endDate": "1972-12-19"
        }

        mocker.patch(
            'source_google_ad_manager.source.create_ad_manager_client',
            side_effect=Exception("Test connection error")
        )

        source = SourceGoogleAdManager()
        result = source.check(logger=mock_logger, config=mock_config)

        # Assert the result is a failed connection
        assert result.status == Status.FAILED
        assert "An exception occurred: Test connection error" in result.message

class TestDiscover:

    def test_discover_returns_expected_catalog(self, mocker):
        # Valid config
        config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": '{"client_email": "fake@example.com", "token_uri": "https://oauth2.googleapis.com/token"}',
            "startDate": "2023-01-01",
            "endDate": "2023-12-31"
        }
        mock_logger = mocker.Mock()
        source = SourceGoogleAdManager()
        catalog = source.discover(mock_logger, config)
        stream = catalog.streams[0]
        
        assert isinstance(catalog, AirbyteCatalog)
        assert len(catalog.streams) == 1
        assert isinstance(stream, AirbyteStream)
        assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
        assert stream.source_defined_cursor is True
        assert stream.default_cursor_field == ["DATE"]
        assert isinstance(stream.json_schema, dict)


class TestRead:

    def test_start_date_greater_than_end_date(self, mocker):
        # Mock logger
        mock_logger = mocker.Mock()
    
        # Invalid config: start date after end date
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": '{"client_email": "fake@example.com", "token_uri": "https://oauth2.googleapis.com/token"}',
            "startDate": "2023-01-31",
            "endDate": "2023-01-01"
        }
    
        # Create instance and call check
        source = SourceGoogleAdManager()
        status = source.check(mock_logger, mock_config)
    
        # Assertions
        assert status.status == Status.FAILED
        assert status.message == "start_date (2023-01-31) cannot be greater than end_date (2023-01-01)."

    # Successfully downloads and processes report data from Google Ad Manager
    def test_successful_report_download_and_processing(self, mocker):
        # Mock dependencies
        mock_logger = mocker.Mock()
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": "{}",
            "startDate": "1972-12-17",
            "endDate": "1972-12-19"
        }
        mock_catalog = mocker.Mock()
        mock_stream = mocker.Mock()
        mock_stream.sync_mode = SyncMode.full_refresh
        mock_stream.stream.name = "google_ad_manager"
        mock_catalog.streams = [mock_stream]

        # Mock Google Ad Manager client and report downloader
        mock_client = mocker.Mock()
        mock_downloader = mocker.Mock()
        mock_downloader.DownloadReportToFile = mocker.Mock(
            side_effect=DownloadReportToFile)
        mock_client.GetDataDownloader.return_value = mock_downloader
        mocker.patch(
            'source_google_ad_manager.source.create_ad_manager_client', return_value=mock_client)
        source = SourceGoogleAdManager()
        messages = list(source.read(
            mock_logger, mock_config, mock_catalog, state={}))

        # Verify expected behavior
        assert len(messages) > 0
        assert messages[0].type == Type.RECORD
        assert messages[0].record.stream == "google_ad_manager"
        assert "DATE" in messages[0].record.data
        assert "record" in messages[0].record.data

        # Verify interactions
        mock_downloader.WaitForReport.assert_called()
        mock_downloader.DownloadReportToFile.assert_called()

    # Empty report file handling
    def test_empty_report_file_handling(self, mocker):
        # Mock dependencies
        mock_logger = mocker.Mock()
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": "{}",
            "startDate": "1972-12-17",
            "endDate": "1972-12-19"
        }
        mock_catalog = mocker.Mock()
        mock_stream = mocker.Mock()
        mock_stream.sync_mode = SyncMode.full_refresh
        mock_stream.stream.name = "google_ad_manager"
        mock_catalog.streams = [mock_stream]

        # Mock Google Ad Manager client and report downloader
        mock_client = mocker.Mock()
        mock_downloader = mocker.Mock()
        mock_downloader.DownloadReportToFile = mocker.Mock()
        mock_client.GetDataDownloader.return_value = mock_downloader
        mocker.patch(
            'source_google_ad_manager.source.create_ad_manager_client', return_value=mock_client)
        source = SourceGoogleAdManager()
        messages = list(source.read(
            mock_logger, mock_config, mock_catalog, state=None))

        # Verify expected behavior
        assert len(messages) == 0
        mock_logger.error.assert_called_with("Temporary report file is empty.")

        # Verify interactions
        mock_downloader.WaitForReport.assert_called()
        mock_downloader.DownloadReportToFile.assert_called()

    # Correctly handles incremental sync mode with state updates
    def test_incremental_sync_with_state_updates(self, mocker):
        # Mock dependencies
        mock_logger = mocker.Mock()
        mock_config = {
            "chunk_size": 1000,
            "network_code": "123456",
            "service_account": "{}",
            "startDate": "2023-01-01",
            "endDate": "2023-01-03"
        }
        mock_catalog = mocker.Mock()
        mock_stream = mocker.Mock()
        mock_stream.sync_mode = SyncMode.incremental
        mock_stream.stream.name = "google_ad_manager"
        mock_catalog.streams = [mock_stream]

        # Mock Google Ad Manager client and report downloader
        mock_client = mocker.Mock()
        mock_downloader = mocker.Mock()
        mock_downloader.DownloadReportToFile = mocker.Mock(
            side_effect=DownloadReportToFile)
        mock_client.GetDataDownloader.return_value = mock_downloader
        mocker.patch(
            'source_google_ad_manager.source.create_ad_manager_client', return_value=mock_client)

        # Mock state
        initial_state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=AirbyteStreamState(
            stream_descriptor=StreamDescriptor(
                name="google_ad_manager", namespace="public"),
            stream_state={"state_date": datetime.strptime("2023-01-02", "%Y-%m-%d"), "start_chunk_index": 0}
        ))]

        source = SourceGoogleAdManager()
        messages = list(source.read(mock_logger, mock_config,
                        mock_catalog, state=initial_state))

        # Verify expected behavior
        assert len(messages) > 0
        assert any(msg.type == Type.RECORD for msg in messages)
        assert any(msg.type == Type.STATE for msg in messages)

        # Verify interactions
        mock_downloader.WaitForReport.assert_called()
        mock_downloader.DownloadReportToFile.assert_called()
