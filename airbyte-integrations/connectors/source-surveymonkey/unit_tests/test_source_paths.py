# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys
from unittest.mock import Mock, patch

from source_surveymonkey.run import _get_source, run


class TestGetSource:
    def test_get_source_success_with_all_paths(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey") as mock_source_class,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_catalog") as mock_read_catalog,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_config") as mock_read_config,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_state") as mock_read_state,
        ):
            # Setup
            mock_extract_catalog.return_value = "catalog_path"
            mock_extract_config.return_value = "config_path"
            mock_extract_state.return_value = "state_path"

            mock_catalog = {"streams": []}
            mock_config = {"access_token": "test"}
            mock_state = {"state": "test"}

            mock_read_catalog.return_value = mock_catalog
            mock_read_config.return_value = mock_config
            mock_read_state.return_value = mock_state

            mock_source_instance = Mock()
            mock_source_class.return_value = mock_source_instance

            # Execute
            result = _get_source(["check", "--config", "config.json", "--catalog", "catalog.json", "--state", "state.json"])

            # Assert
            assert result == mock_source_instance
            mock_read_catalog.assert_called_once_with("catalog_path")
            mock_read_config.assert_called_once_with("config_path")
            mock_read_state.assert_called_once_with("state_path")
            mock_source_class.assert_called_once_with(mock_catalog, mock_config, mock_state)

    def test_get_source_success_with_none_paths(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey") as mock_source_class,
        ):
            # Setup
            mock_extract_catalog.return_value = None
            mock_extract_config.return_value = None
            mock_extract_state.return_value = None
            mock_source_instance = Mock()
            mock_source_class.return_value = mock_source_instance

            # Execute
            result = _get_source(["check"])

            # Assert
            assert result == mock_source_instance
            mock_source_class.assert_called_once_with(None, None, None)

    def test_get_source_handles_exception(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey") as mock_source_class,
            patch("source_surveymonkey.run.print") as mock_print,
            patch("source_surveymonkey.run.datetime") as mock_datetime,
        ):
            # Setup
            mock_extract_catalog.return_value = None
            mock_extract_config.return_value = None
            mock_extract_state.return_value = None
            mock_source_class.side_effect = Exception("Test error")
            mock_datetime.now.return_value.timestamp.return_value = 1234567890.123

            # Execute
            result = _get_source(["check"])

            # Assert
            assert result is None
            mock_print.assert_called_once()
            # Verify the printed message contains error information
            printed_args = mock_print.call_args[0][0]
            assert "Test error" in printed_args
            assert "TRACE" in printed_args

    def test_get_source_handles_config_read_exception(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_config") as mock_read_config,
            patch("source_surveymonkey.run.print") as mock_print,
        ):
            # Setup
            mock_extract_catalog.return_value = None
            mock_extract_config.return_value = "config_path"
            mock_extract_state.return_value = None
            mock_read_config.side_effect = Exception("Config read error")

            # Execute
            result = _get_source(["check", "--config", "config.json"])

            # Assert
            assert result is None
            mock_print.assert_called_once()

    def test_get_source_handles_catalog_read_exception(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_catalog") as mock_read_catalog,
            patch("source_surveymonkey.run.print") as mock_print,
        ):
            # Setup
            mock_extract_catalog.return_value = "catalog_path"
            mock_extract_config.return_value = None
            mock_extract_state.return_value = None
            mock_read_catalog.side_effect = Exception("Catalog read error")

            # Execute
            result = _get_source(["check", "--catalog", "catalog.json"])

            # Assert
            assert result is None
            mock_print.assert_called_once()

    def test_get_source_handles_state_read_exception(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_state") as mock_read_state,
            patch("source_surveymonkey.run.print") as mock_print,
        ):
            # Setup
            mock_extract_catalog.return_value = None
            mock_extract_config.return_value = None
            mock_extract_state.return_value = "state_path"
            mock_read_state.side_effect = Exception("State read error")

            # Execute
            result = _get_source(["check", "--state", "state.json"])

            # Assert
            assert result is None
            mock_print.assert_called_once()

    def test_get_source_partial_paths(self):
        with (
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_catalog") as mock_extract_catalog,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_config") as mock_extract_config,
            patch("source_surveymonkey.run.AirbyteEntrypoint.extract_state") as mock_extract_state,
            patch("source_surveymonkey.run.SourceSurveymonkey") as mock_source_class,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_catalog") as mock_read_catalog,
            patch("source_surveymonkey.run.SourceSurveymonkey.read_config") as mock_read_config,
        ):
            # Setup - only config and catalog paths provided
            mock_extract_catalog.return_value = "catalog_path"
            mock_extract_config.return_value = "config_path"
            mock_extract_state.return_value = None

            mock_catalog = {"streams": []}
            mock_config = {"access_token": "test"}

            mock_read_catalog.return_value = mock_catalog
            mock_read_config.return_value = mock_config

            mock_source_instance = Mock()
            mock_source_class.return_value = mock_source_instance

            # Execute
            result = _get_source(["check", "--config", "config.json", "--catalog", "catalog.json"])

            # Assert
            assert result == mock_source_instance
            mock_read_catalog.assert_called_once_with("catalog_path")
            mock_read_config.assert_called_once_with("config_path")
            mock_source_class.assert_called_once_with(mock_catalog, mock_config, None)


class TestRun:
    @patch("source_surveymonkey.run._get_source")
    @patch("source_surveymonkey.run.launch")
    def test_run_with_none_source(self, mock_launch, mock_get_source):
        # Setup
        mock_get_source.return_value = None
        original_argv = sys.argv
        sys.argv = ["run.py", "check"]

        try:
            # Execute
            run()

            # Assert
            mock_get_source.assert_called_once_with(["check"])
            mock_launch.assert_not_called()
        finally:
            sys.argv = original_argv

    @patch("source_surveymonkey.run._get_source")
    @patch("source_surveymonkey.run.launch")
    def test_run_with_empty_args(self, mock_launch, mock_get_source):
        # Setup
        mock_source = Mock()
        mock_get_source.return_value = mock_source
        original_argv = sys.argv
        sys.argv = ["run.py"]

        try:
            # Execute
            run()

            # Assert
            mock_get_source.assert_called_once_with([])
            mock_launch.assert_called_once_with(mock_source, [])
        finally:
            sys.argv = original_argv
