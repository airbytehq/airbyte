#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

import pytest
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

    mock_smart_open.assert_called_once_with(mock_file.download_url, mode="r", encoding="utf-8")
    assert result is not None


def test_microsoft_onedrive_client_initialization(requests_mock):
    """Test the initialization of SourceMicrosoftOneDriveClient."""
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

    with patch.object(SourceMicrosoftOneDriveStreamReader, "drives", new_callable=PropertyMock) as mock_drives:
        mock_drives.return_value = [mock_drive]

        # Call the method
        files = list(stream_reader.get_files_by_drive_name("testDrive", "/test/path"))

    # Assertions
    assert len(files) == 1
    assert files[0].name == "testFile.txt"


@pytest.mark.parametrize(
    "selected_drive_id, drive_ids, shared_drive_item_dicts, expected_result, expected_calls",
    [
        (None, [1, 2, 3], [], [], []),
        (1, [1, 2, 3], [{"drive_id": 1, "id": 4, "web_url": "test_url4"}], [], []),
        (1, [1, 2, 3], [{"drive_id": 4, "id": 4, "web_url": "test_url4"}], [4], [call(4, 4, "test_url4")]),
        (
            2,
            [1, 2, 3],
            [{"drive_id": 4, "id": 4, "web_url": "test_url4"}, {"drive_id": 5, "id": 5, "web_url": "test_url5"}],
            [4, 5],
            [call(4, 4, "test_url4"), call(5, 5, "test_url5")],
        ),
        (
            3,
            [1, 2, 3],
            [
                {"drive_id": 4, "id": 4, "web_url": "test_url4"},
                {"drive_id": 5, "id": 5, "web_url": "test_url5"},
                {"drive_id": 6, "id": 6, "web_url": "test_url6"},
            ],
            [4, 5, 6],
            [call(4, 4, "test_url4"), call(5, 5, "test_url5"), call(6, 6, "test_url6")],
        ),
    ],
)
def test_get_shared_files_from_all_drives(selected_drive_id, drive_ids, shared_drive_item_dicts, expected_result, expected_calls):
    stream_reader = SourceMicrosoftOneDriveStreamReader()
    stream_reader._config = Mock()

    # Mock _get_shared_drive_object method
    with patch.object(
        SourceMicrosoftOneDriveStreamReader, "_get_shared_drive_object", return_value=expected_result
    ) as mock_get_shared_drive_object:
        # Setup shared_drive_items mock objects
        shared_drive_items = [
            MagicMock(remote_item=MagicMock(parentReference={"driveId": item["drive_id"]}), id=item["id"], web_url=item["web_url"])
            for item in shared_drive_item_dicts
        ]

        with patch.object(SourceMicrosoftOneDriveStreamReader, "one_drive_client", new_callable=PropertyMock) as mock_one_drive_client:
            mock_one_drive_client.return_value.me.drive.shared_with_me.return_value.execute_query.return_value = shared_drive_items

            with patch.object(SourceMicrosoftOneDriveStreamReader, "drives", new_callable=PropertyMock) as mock_drives:
                mock_drives.return_value = [Mock(id=drive_id) for drive_id in drive_ids]

                # Execute the method under test
                list(stream_reader._get_shared_files_from_all_drives(selected_drive_id))

                # Assert _get_shared_drive_object was called correctly
                mock_get_shared_drive_object.assert_has_calls(expected_calls, any_order=True)


# Sample data for mocking responses
file_response = {
    "file": True,
    "name": "TestFile.txt",
    "@microsoft.graph.downloadUrl": "http://example.com/download",
    "lastModifiedDateTime": "2021-01-01T00:00:00Z",
}

empty_folder_response = {"folder": True, "value": []}

# Adjusting the folder_with_nested_files to represent the initial folder response
folder_with_nested_files_initial = {
    "folder": True,
    "value": [
        {"id": "subfolder1", "folder": True, "name": "subfolder1"},
        {"id": "subfolder2", "folder": True, "name": "subfolder2"},
    ],  # Empty subfolder  # Subfolder with a file
}

# Response for the empty subfolder (subfolder1)
empty_subfolder_response = {"value": [], "name": "subfolder1"}  # No files or folders inside subfolder1

# Response for the subfolder with a file (subfolder2)
not_empty_subfolder_response = {
    "value": [
        {
            "file": True,
            "name": "NestedFile.txt",
            "@microsoft.graph.downloadUrl": "http://example.com/nested",
            "lastModifiedDateTime": "2021-01-02T00:00:00Z",
        }
    ],
    "name": "subfolder2",
}


@pytest.mark.parametrize(
    "initial_response, subsequent_responses, expected_result, raises_error, expected_error_message, initial_path",
    [
        # Object ID is a file
        (
            file_response,
            [],
            [
                (
                    "http://example.com/TestFile.txt",
                    "http://example.com/download",
                    datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                )
            ],
            False,
            None,
            "http://example.com",
        ),
        # Object ID is an empty folder
        (empty_folder_response, [empty_subfolder_response], [], False, None, "http://example.com"),
        # Object ID is a folder with empty subfolders and files
        (
            {"folder": True, "name": "root"},  # Initial folder response
            [
                folder_with_nested_files_initial,
                empty_subfolder_response,
                not_empty_subfolder_response,
            ],
            [
                (
                    "http://example.com/subfolder2/NestedFile.txt",
                    "http://example.com/nested",
                    datetime.strptime("2021-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
                )
            ],
            False,
            None,
            "http://example.com",
        ),
        # Error response on initial request
        (
            MagicMock(status_code=400, json=MagicMock(return_value={"error": {"message": "Bad Request"}})),
            [],
            [],
            True,
            "Failed to retrieve the initial shared object with ID 'dummy_object_id' from drive 'dummy_drive_id'. HTTP status: 400. Error: Bad Request",
            "http://example.com",
        ),
        # Error response while iterating over nested
        (
            {"folder": True, "name": "root"},
            [MagicMock(status_code=400, json=MagicMock(return_value={"error": {"message": "Bad Request"}}))],
            [],
            True,
            (
                "Failed to retrieve files from URL "
                "'https://graph.microsoft.com/v1.0/drives/dummy_drive_id/items/dummy_object_id/children'. "
                "HTTP status: 400. Error: Bad Request"
            ),
            "http://example.com",
        ),
    ],
)
@patch("source_microsoft_onedrive.stream_reader.requests.get")
@patch("source_microsoft_onedrive.stream_reader.SourceMicrosoftOneDriveStreamReader.get_access_token")
def test_get_shared_drive_object(
    mock_get_access_token,
    mock_requests_get,
    initial_response,
    subsequent_responses,
    expected_result,
    raises_error,
    expected_error_message,
    initial_path,
):
    mock_get_access_token.return_value = "dummy_access_token"
    mock_responses = [
        initial_response
        if isinstance(initial_response, MagicMock)
        else MagicMock(status_code=200, json=MagicMock(return_value=initial_response))
    ]
    for response in subsequent_responses:
        mock_responses.append(
            response if isinstance(response, MagicMock) else MagicMock(status_code=200, json=MagicMock(return_value=response))
        )
    mock_requests_get.side_effect = mock_responses

    reader = SourceMicrosoftOneDriveStreamReader()

    if raises_error:
        with pytest.raises(RuntimeError) as exc_info:
            list(reader._get_shared_drive_object("dummy_drive_id", "dummy_object_id", initial_path))
        assert str(exc_info.value) == expected_error_message
    else:
        result = list(reader._get_shared_drive_object("dummy_drive_id", "dummy_object_id", initial_path))
        assert result == expected_result
