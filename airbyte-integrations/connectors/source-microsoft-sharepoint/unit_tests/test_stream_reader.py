#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from msal.exceptions import MsalServiceError
from source_microsoft_sharepoint.spec import SourceMicrosoftSharePointSpec
from source_microsoft_sharepoint.stream_reader import (
    FileReadMode,
    MicrosoftSharePointRemoteFile,
    SourceMicrosoftSharePointClient,
    SourceMicrosoftSharePointStreamReader,
)
from wcmatch.glob import GLOBSTAR, globmatch


def create_mock_drive_item(is_file, name, children=None):
    """Helper function to create a mock drive item."""
    mock_item = Mock()
    mock_item.is_file = is_file
    mock_item.name = name
    mock_item.children.get.return_value.execute_query = Mock(return_value=children or [])
    return mock_item


@pytest.fixture
def setup_reader_class():
    reader = SourceMicrosoftSharePointStreamReader()  # Instantiate your class here
    config = Mock(spec=SourceMicrosoftSharePointSpec)
    config.start_date = None
    config.credentials = Mock()
    config.folder_path = "."
    config.credentials.auth_type = "Client"
    reader.config = config  # Set up the necessary configuration

    # Mock the client creation
    with patch("source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.client = Mock()  # Mock the client attribute of SourceMicrosoftSharePointClient
        yield reader


@pytest.fixture
def mock_drive_files():
    # Mock files returned by SharePoint
    return [
        Mock(
            properties={
                "@microsoft.graph.downloadUrl": "https://example.com/file1.csv",
                "lastModifiedDateTime": datetime.datetime(2021, 1, 1),
            }
        ),
        Mock(
            properties={
                "@microsoft.graph.downloadUrl": "https://example.com/file2.txt",
                "lastModifiedDateTime": datetime.datetime(2021, 1, 1),
            }
        ),
    ]


@pytest.fixture
def setup_client_class():
    config = Mock(spec=SourceMicrosoftSharePointSpec)
    config.credentials = Mock()
    config.folder_path = "."
    config.credentials.auth_type = "Client"

    with patch("source_microsoft_sharepoint.stream_reader.ConfidentialClientApplication") as mock_client_class:
        mock_msal_app_instance = Mock()
        mock_client_class.return_value = mock_msal_app_instance

        client_class = SourceMicrosoftSharePointClient(config)

        yield client_class


@pytest.mark.parametrize(
    "has_refresh_token, token_response, expected_result, raises_exception",
    [
        (False, {"access_token": "test_access_token"}, {"access_token": "test_access_token"}, False),
        (True, {"access_token": "test_access_token"}, {"access_token": "test_access_token"}, False),
        (False, {"error": "test_error", "error_description": "test_error_description"}, None, True),
    ],
)
def test_get_access_token(setup_client_class, has_refresh_token, token_response, expected_result, raises_exception):
    instance = setup_client_class
    if has_refresh_token:
        instance.config.credentials.refresh_token = "test_refresh_token"
        instance._msal_app.acquire_token_by_refresh_token.return_value = token_response
    else:
        instance.config.credentials.refresh_token = None
        instance._msal_app.acquire_token_for_client.return_value = token_response

    if raises_exception:
        with pytest.raises(AirbyteTracedException) as exception:
            instance._get_access_token()
        assert exception.value.message == f"Failed to acquire access token. Error: test_error. Error description: test_error_description."
    else:
        assert instance._get_access_token() == expected_result

        if has_refresh_token:
            instance._msal_app.acquire_token_by_refresh_token.assert_called_once_with(
                "test_refresh_token", scopes=["https://graph.microsoft.com/.default"]
            )
        else:
            instance._msal_app.acquire_token_for_client.assert_called_once_with(scopes=["https://graph.microsoft.com/.default"])


@patch("source_microsoft_sharepoint.stream_reader.execute_query_with_retry")
@patch("source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader.filter_files_by_globs_and_start_date")
def test_get_matching_files(mock_filter_files, mock_execute_query, setup_reader_class, mock_drive_files):
    instance = setup_reader_class
    instance._get_files_by_drive_name = Mock(return_value=iter([(mock_drive_files[0], "file1.csv"), (mock_drive_files[1], "file2.txt")]))

    # Set up mocks
    mock_drive = Mock()
    mock_drive.get.return_value = mock_drive
    mock_execute_query.return_value = mock_drive
    mock_filter_files.side_effect = lambda files, globs: (f for f in files if any(globmatch(f.uri, g, flags=GLOBSTAR) for g in globs))

    # Define test parameters
    globs = ["*.csv"]
    prefix = None
    logger = Mock()

    # Call the method
    files = list(instance.get_matching_files(globs, prefix, logger))

    # Assertions
    assert len(files) == 1
    assert isinstance(files[0], MicrosoftSharePointRemoteFile)
    assert files[0].uri == "file1.csv"
    assert "https://example.com/file1.csv" in files[0].download_url


def test_get_matching_files_empty_drive(setup_reader_class):
    instance = setup_reader_class
    instance._get_files_by_drive_name = Mock(return_value=iter([]))

    # Define test parameters
    globs = ["*.csv"]
    prefix = None
    logger = Mock()

    # Expecting an exception when drive is empty
    with pytest.raises(AirbyteTracedException):
        list(instance.get_matching_files(globs, prefix, logger))


@pytest.mark.parametrize(
    "file_extension, expected_compression",
    [
        (".txt.gz", ".gz"),
        (".txt.bz2", ".bz2"),
        ("txt", "disable"),
    ],
)
@patch("smart_open.open")
def test_open_file(mock_smart_open, file_extension, expected_compression):
    """Test the open_file method in SourceMicrosoftSharePointStreamReader."""
    mock_file = Mock(download_url=f"https://example.com/file.{file_extension}", uri=f"file.{file_extension}")
    mock_logger = Mock()

    stream_reader = SourceMicrosoftSharePointStreamReader()
    stream_reader._config = Mock()  # Assuming _config is required

    with stream_reader.open_file(mock_file, FileReadMode.READ, "utf-8", mock_logger) as result:
        pass

    mock_smart_open.assert_called_once_with(mock_file.download_url, mode="r", encoding="utf-8", compression=expected_compression)
    assert result is not None


def test_microsoft_sharepoint_client_initialization(requests_mock):
    """Test the initialization of SourceMicrosoftSharePointClient."""
    config = {
        "credentials": {
            "auth_type": "Client",
            "client_id": "client_id",
            "tenant_id": "tenant_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
        },
        "drive_name": "drive_name",
        "folder_path": "folder_path",
        "streams": [{"name": "test_stream", "globs": ["*.csv"], "validation_policy": "Emit Record", "format": {"filetype": "csv"}}],
    }

    authority_url = "https://login.microsoftonline.com/tenant_id/v2.0/.well-known/openid-configuration"
    mock_response = {
        "authorization_endpoint": "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/authorize",
        "token_endpoint": "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
    }
    requests_mock.get(authority_url, json=mock_response, status_code=200)

    client = SourceMicrosoftSharePointClient(SourceMicrosoftSharePointSpec(**config))

    assert client.config == SourceMicrosoftSharePointSpec(**config)
    assert client._msal_app is not None


def test_list_directories_and_files():
    """Test the list_directories_and_files method in SourceMicrosoftSharePointStreamReader."""
    # Create a mock structure of folders and files
    mock_child_file1 = create_mock_drive_item(True, "file1.txt")
    mock_child_file2 = create_mock_drive_item(True, "file2.txt")
    mock_child_folder = create_mock_drive_item(False, "folder1", children=[mock_child_file1])
    mock_root_folder = create_mock_drive_item(False, "root", children=[mock_child_folder, mock_child_file2])

    stream_reader = SourceMicrosoftSharePointStreamReader()

    result = stream_reader._list_directories_and_files(mock_root_folder)

    assert len(result) == 2
    assert result[0][1] == "folder1/file1.txt"
    assert result[1][1] == "file2.txt"


@pytest.mark.parametrize(
    "drive_type, files_number",
    [
        ("documentLibrary", 1),
        ("business", 0),
    ],
)
@patch("source_microsoft_sharepoint.stream_reader.SourceMicrosoftSharePointStreamReader._list_directories_and_files")
def test_get_files_by_drive_name(mock_list_directories_and_files, drive_type, files_number):
    # Helper function usage
    mock_drive = Mock()
    mock_drive.name = "testDrive"
    mock_drive.drive_type = drive_type
    mock_drive.root.get_by_path.return_value.get().execute_query_with_incremental_retry.return_value = create_mock_drive_item(
        is_file=False, name="root"
    )

    # Mock files
    mock_file = create_mock_drive_item(is_file=True, name="testFile.txt")
    mock_list_directories_and_files.return_value = [mock_file]

    # Create stream reader instance
    stream_reader = SourceMicrosoftSharePointStreamReader()
    stream_reader._config = Mock()

    # Call the method
    files = list(stream_reader._get_files_by_drive_name([mock_drive], "/test/path"))

    # Assertions
    assert len(files) == files_number
    if files_number:
        assert files[0].name == "testFile.txt"
