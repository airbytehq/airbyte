#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

from source_microsoft_onedrive.spec import SourceMicrosoftOneDriveSpec
from source_microsoft_onedrive.stream_reader import FileReadMode, SourceMicrosoftOneDriveClient, SourceMicrosoftOneDriveStreamReader


def create_mock_drive_item(is_file, name):
    """Helper function to create a mock drive item."""
    mock_item = Mock()
    mock_item.is_file = is_file
    mock_item.name = name
    return mock_item


@patch("smart_open.open")
def test_open_file(mock_smart_open):
    """Test the open_file method in SourceMicrosoftOneDriveStreamReader."""
    mock_file = Mock(download_url="http://example.com/file.txt")
    mock_logger = Mock()

    stream_reader = SourceMicrosoftOneDriveStreamReader()
    stream_reader._config = Mock()  # Assuming _config is required

    with stream_reader.open_file(mock_file, FileReadMode.READ, "utf-8", mock_logger) as result:
        pass

    mock_smart_open.assert_called_once_with(mock_file.download_url, mode='r', encoding='utf-8')
    assert result is not None


def test_microsoft_onedrive_client_initialization(requests_mock):
    """Test the initialization of SourceMicrosoftOneDriveClient."""
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

    client = SourceMicrosoftOneDriveClient(SourceMicrosoftOneDriveSpec(**config))

    assert client.config == SourceMicrosoftOneDriveSpec(**config)
    assert client.msal_app is not None


@patch("source_microsoft_onedrive.stream_reader.SourceMicrosoftOneDriveStreamReader.list_directories_and_files")
def test_list_directories_and_files(mock_list_directories_and_files):
    """Test the list_directories_and_files method in SourceMicrosoftOneDriveStreamReader."""
    mock_root_folder = create_mock_drive_item(False, "root")
    mock_child_file = create_mock_drive_item(True, "file1.txt")
    mock_child_folder = create_mock_drive_item(False, "folder1")
    mock_child_folder.children.get().execute_query.return_value = [mock_child_file]
    mock_root_folder.children.get().execute_query.return_value = [mock_child_folder, mock_child_file]

    mock_list_directories_and_files.return_value = [mock_child_folder, mock_child_file]

    stream_reader = SourceMicrosoftOneDriveStreamReader()
    result = stream_reader.list_directories_and_files(mock_root_folder)

    assert len(result) == 2
    assert result[0].name == "folder1"
    assert result[1].name == "file1.txt"


@patch("source_microsoft_onedrive.stream_reader.SourceMicrosoftOneDriveStreamReader.list_directories_and_files")
def test_get_files_by_drive_name(mock_list_directories_and_files):
    # Helper function usage
    mock_drive = Mock()
    mock_drive.name = "testDrive"
    mock_drive.drive_type = "business"
    mock_drive.root.get_by_path.return_value.get().execute_query.return_value = create_mock_drive_item(is_file=False, name="root")

    # Mock files
    mock_file = create_mock_drive_item(is_file=True, name="testFile.txt")
    mock_list_directories_and_files.return_value = [mock_file]

    # Create stream reader instance
    stream_reader = SourceMicrosoftOneDriveStreamReader()
    stream_reader._config = Mock()

    # Call the method
    files = list(stream_reader.get_files_by_drive_name([mock_drive], "testDrive", "/test/path"))

    # Assertions
    assert len(files) == 1
    assert files[0].name == "testFile.txt"
