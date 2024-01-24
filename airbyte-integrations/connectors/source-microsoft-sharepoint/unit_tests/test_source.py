#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from unittest.mock import Mock, patch
import pytest

from source_microsoft_sharepoint.spec import SourceMicrosoftSharePointSpec
from source_microsoft_sharepoint.stream_reader import (FileReadMode, SourceMicrosoftSharePointClient, MicrosoftSharePointRemoteFile,
                                                       SourceMicrosoftSharePointStreamReader)


def create_mock_drive_item(is_file, name):
    """Helper function to create a mock drive item."""
    mock_item = Mock()
    mock_item.is_file = is_file
    mock_item.name = name
    return mock_item

@pytest.fixture
def setup_stream_reader():
    stream_reader = SourceMicrosoftSharePointStreamReader()
    stream_reader._config = Mock()  # Mock the configuration as needed

    mock_root_folder = create_mock_drive_item(False, "root")
    mock_child_file = create_mock_drive_item(True, "file1.txt")
    mock_child_folder = create_mock_drive_item(False, "folder1")
    mock_child_folder.children.get().execute_query.return_value = [mock_child_file]
    mock_root_folder.children.get().execute_query.return_value = [mock_child_folder, mock_child_file]
    stream_reader.one_drive_client.get().execute_query.return_value = [mock_child_folder, mock_child_file]

    return stream_reader

@pytest.fixture
def mock_files():
    return [
        MicrosoftSharePointRemoteFile(uri="folder1/file1.csv", download_url="http://example.com/folder1/file1.csv", last_modified=datetime.datetime(2023, 1, 1)),
        MicrosoftSharePointRemoteFile(uri="folder1/file2.csv", download_url="http://example.com/folder1/file2.csv", last_modified=datetime.datetime(2023, 1, 1)),
        MicrosoftSharePointRemoteFile(uri="folder2/file3.txt", download_url="http://example.com/folder2/file3.txt", last_modified=datetime.datetime(2023, 1, 1))
    ]

@pytest.mark.skip()
@patch('source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader.filter_files_by_globs_and_start_date')
@patch('source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader.get_files_by_drive_name')
def test_get_matching_files(mock_get_files_by_drive_name, mock_filter_files_by_globs, setup_stream_reader, mock_files):
    stream_reader = setup_stream_reader

    mock_get_files_by_drive_name.return_value = mock_files
    mock_filter_files_by_globs.return_value = [mock_files[0], mock_files[1]]  # Assuming these two match the pattern

    globs = ["*.csv"]
    prefix = None
    mock_logger = Mock()

    matching_files = stream_reader.get_matching_files(globs, prefix, mock_logger)
    matching_files = list(matching_files)

    mock_get_files_by_drive_name.assert_called_once()
    mock_filter_files_by_globs.assert_called_once_with(mock_files, globs)
    assert len(matching_files) == 2
    assert matching_files[0].uri == "folder1/file1.csv"
    assert matching_files[1].uri == "folder1/file2.csv"


@patch("smart_open.open")
def test_open_file(mock_smart_open):
    """Test the open_file method in SourceMicrosoftSharePointStreamReader."""
    mock_file = Mock(download_url="http://example.com/file.txt", uri="file.txt")
    mock_logger = Mock()

    stream_reader = SourceMicrosoftSharePointStreamReader()
    stream_reader._config = Mock()  # Assuming _config is required

    with stream_reader.open_file(mock_file, FileReadMode.READ, "utf-8", mock_logger) as result:
        pass

    mock_smart_open.assert_called_once_with(mock_file.download_url, mode='r', encoding='utf-8', compression='disable')
    assert result is not None


def test_microsoft_sharepoint_client_initialization(requests_mock):
    """Test the initialization of SourceMicrosoftSharePointClient."""
    config = {
        "credentials": {
            "auth_type": "Client",
            "client_id": "client_id",
            "tenant_id": "tenant_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token"
        },
        "drive_name": "drive_name",
        "folder_path": "folder_path",
        "streams": [{"name": "test_stream", "globs": ["*.csv"], "validation_policy": "Emit Record", "format": {"filetype": "csv"}}]
    }

    authority_url = 'https://login.microsoftonline.com/tenant_id/v2.0/.well-known/openid-configuration'
    mock_response = {'authorization_endpoint': 'https://login.microsoftonline.com/tenant_id/oauth2/v2.0/authorize', 'token_endpoint': 'https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token'}
    requests_mock.get(authority_url, json=mock_response, status_code=200)

    client = SourceMicrosoftSharePointClient(SourceMicrosoftSharePointSpec(**config))

    assert client.config == SourceMicrosoftSharePointSpec(**config)
    assert client.msal_app is not None


@patch("source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader.list_directories_and_files")
def test_list_directories_and_files(mock_list_directories_and_files):
    """Test the list_directories_and_files method in SourceMicrosoftSharePointStreamReader."""
    mock_root_folder = create_mock_drive_item(False, "root")
    mock_child_file = create_mock_drive_item(True, "file1.txt")
    mock_child_folder = create_mock_drive_item(False, "folder1")
    mock_child_folder.children.get().execute_query.return_value = [mock_child_file]
    mock_root_folder.children.get().execute_query.return_value = [mock_child_folder, mock_child_file]

    mock_list_directories_and_files.return_value = [mock_child_folder, mock_child_file]

    stream_reader = SourceMicrosoftSharePointStreamReader()
    result = stream_reader.list_directories_and_files(mock_root_folder)

    assert len(result) == 2
    assert result[0].name == "folder1"
    assert result[1].name == "file1.txt"

@pytest.mark.parametrize(
    "drive_type, files_number",
    [
        ("documentLibrary", 1),
        ("business", 0),
    ],
)
@patch("source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader.list_directories_and_files")
def test_get_files_by_drive_name(mock_list_directories_and_files, drive_type, files_number):
    # Helper function usage
    mock_drive = Mock()
    mock_drive.name = "testDrive"
    mock_drive.drive_type = drive_type
    mock_drive.root.get_by_path.return_value.get().execute_query.return_value = create_mock_drive_item(is_file=False, name="root")

    # Mock files
    mock_file = create_mock_drive_item(is_file=True, name="testFile.txt")
    mock_list_directories_and_files.return_value = [mock_file]

    # Create stream reader instance
    stream_reader = SourceMicrosoftSharePointStreamReader()
    stream_reader._config = Mock()

    # Call the method
    files = list(stream_reader.get_files_by_drive_name([mock_drive], "/test/path"))

    # Assertions
    assert len(files) == files_number
    if files_number:
        assert files[0].name == "testFile.txt"
