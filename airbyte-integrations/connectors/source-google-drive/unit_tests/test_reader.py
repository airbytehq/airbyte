#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
from unittest.mock import MagicMock, call, patch

import pytest
from source_google_drive.spec import ServiceAccountCredentials, SourceGoogleDriveSpec
from source_google_drive.stream_reader import GoogleDriveRemoteFile, SourceGoogleDriveStreamReader

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode


def create_reader(
    config=SourceGoogleDriveSpec(
        folder_url="https://drive.google.com/drive/folders/1Z2Q3",
        streams=[FileBasedStreamConfig(name="test", format=JsonlFormat())],
        credentials=ServiceAccountCredentials(auth_type="Service", service_account_info='{"test": "abc"}'),
    ),
):
    reader = SourceGoogleDriveStreamReader()
    reader.config = config

    return reader


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


@pytest.mark.parametrize(
    "glob, listing_results, matched_files",
    [
        pytest.param(
            "*",
            [[{"files": [{"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"}]}]],
            [
                GoogleDriveRemoteFile(
                    uri="test.csv",
                    id="abc",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                )
            ],
            id="Single file",
        ),
        pytest.param(
            "*",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                        ]
                    },
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="test.csv",
                    id="abc",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
                GoogleDriveRemoteFile(
                    uri="another_file.csv",
                    id="def",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Multiple files",
        ),
        pytest.param(
            "*",
            [
                [
                    {"files": [{"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"}]},
                    {
                        "files": [
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"}
                        ]
                    },
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="test.csv",
                    id="abc",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
                GoogleDriveRemoteFile(
                    uri="another_file.csv",
                    id="def",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Multiple pages",
        ),
        pytest.param(
            "*",
            [
                [
                    {"files": []},
                ]
            ],
            [],
            id="No files",
        ),
        pytest.param(
            "**/*",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # second request is for requesting the subfolder
                    {
                        "files": [
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "subsub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subsubfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # third request is for requesting the subsubfolder
                    {
                        "files": [
                            {
                                "id": "ghi",
                                "mimeType": "text/csv",
                                "name": "yet_another_file.csv",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
            ],
            [
                GoogleDriveRemoteFile(
                    uri="test.csv",
                    id="abc",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
                GoogleDriveRemoteFile(
                    uri="subfolder/another_file.csv",
                    id="def",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
                GoogleDriveRemoteFile(
                    uri="subfolder/subsubfolder/yet_another_file.csv",
                    id="ghi",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Nested directories",
        ),
        pytest.param(
            "**/*",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # second request is for requesting the subfolder
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "subsub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subsubfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # third request is for requesting the subsubfolder
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "link_to_subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
            ],
            [
                GoogleDriveRemoteFile(
                    uri="test.csv",
                    id="abc",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Duplicates",
        ),
        pytest.param(
            "subfolder/**/*.csv",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # second request is for requesting the subfolder
                    {
                        "files": [
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "ghi",
                                "mimeType": "text/jsonl",
                                "name": "non_matching.jsonl",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
            ],
            [
                GoogleDriveRemoteFile(
                    uri="subfolder/another_file.csv",
                    id="def",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Glob matching and subdirectories",
        ),
        pytest.param(
            "subfolder/*.csv",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                            # This won't get queued because it has no chance of matching the glob
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "ignored_subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # second request is for requesting the subfolder
                    {
                        "files": [
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            # This will get queued because it matches the prefix (event though it can't match the glob)
                            {
                                "id": "subsub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subsubfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # third request is for requesting the subsubfolder
                    {
                        "files": [
                            {
                                "id": "ghi",
                                "mimeType": "text/csv",
                                "name": "yet_another_file.csv",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
            ],
            [
                GoogleDriveRemoteFile(
                    uri="subfolder/another_file.csv",
                    id="def",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Glob matching and ignoring most subdirectories that can't be matched",
        ),
        pytest.param(
            "subfolder/subsubfolder/*.csv",
            [
                [
                    {
                        "files": [
                            {"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            {
                                "id": "sub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # second request is for requesting the subfolder
                    {
                        "files": [
                            {"id": "def", "mimeType": "text/csv", "name": "another_file.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"},
                            # This will get queued because it matches the prefix (event though it can't match the glob)
                            {
                                "id": "subsub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "subsubfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [
                    # third request is for requesting the subsubfolder
                    {
                        "files": [
                            {
                                "id": "ghi",
                                "mimeType": "text/csv",
                                "name": "yet_another_file.csv",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                            # This will get queued because it matches the prefix (event though it can't match the glob)
                            {
                                "id": "subsubsub",
                                "mimeType": "application/vnd.google-apps.folder",
                                "name": "ignored_subsubsubfolder",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            },
                        ]
                    },
                ],
                [{"files": []}],
            ],
            [
                GoogleDriveRemoteFile(
                    uri="subfolder/subsubfolder/yet_another_file.csv",
                    id="ghi",
                    mime_type="text/csv",
                    original_mime_type="text/csv",
                    last_modified=datetime.datetime(2021, 1, 1),
                ),
            ],
            id="Glob matching and ignoring subdirectories that can't be matched, multiple levels",
        ),
        pytest.param(
            "*",
            [
                [
                    {
                        "files": [
                            {
                                "id": "abc",
                                "mimeType": "application/vnd.google-apps.document",
                                "name": "MyDoc",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            }
                        ]
                    }
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="MyDoc",
                    id="abc",
                    original_mime_type="application/vnd.google-apps.document",
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    last_modified=datetime.datetime(2021, 1, 1),
                )
            ],
            id="Google Doc as docx",
        ),
        pytest.param(
            "*",
            [
                [
                    {
                        "files": [
                            {
                                "id": "abc",
                                "mimeType": "application/vnd.google-apps.presentation",
                                "name": "MySlides",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            }
                        ]
                    }
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="MySlides",
                    id="abc",
                    original_mime_type="application/vnd.google-apps.presentation",
                    mime_type="application/pdf",
                    last_modified=datetime.datetime(2021, 1, 1),
                )
            ],
            id="Presentation as pdf",
        ),
        pytest.param(
            "*",
            [
                [
                    {
                        "files": [
                            {
                                "id": "abc",
                                "mimeType": "application/vnd.google-apps.drawing",
                                "name": "MyDrawing",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            }
                        ]
                    }
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="MyDrawing",
                    id="abc",
                    original_mime_type="application/vnd.google-apps.drawing",
                    mime_type="application/pdf",
                    last_modified=datetime.datetime(2021, 1, 1),
                )
            ],
            id="Drawing as pdf",
        ),
        pytest.param(
            "*",
            [
                [
                    {
                        "files": [
                            {
                                "id": "abc",
                                "mimeType": "application/vnd.google-apps.video",
                                "name": "MyVideo",
                                "modifiedTime": "2021-01-01T00:00:00.000Z",
                            }
                        ]
                    }
                ]
            ],
            [
                GoogleDriveRemoteFile(
                    uri="MyVideo",
                    id="abc",
                    original_mime_type="application/vnd.google-apps.video",
                    mime_type="application/vnd.google-apps.video",
                    last_modified=datetime.datetime(2021, 1, 1),
                )
            ],
            id="Other google file types as is",
        ),
    ],
)
@patch("source_google_drive.stream_reader.service_account")
@patch("source_google_drive.stream_reader.build")
def test_matching_files(mock_build_service, mock_service_account, glob, listing_results, matched_files):
    mock_request = MagicMock()
    # execute returns all results from all pages for all listings
    flattened_results = flatten_list(listing_results)

    mock_request.execute.side_effect = flattened_results
    files_service = MagicMock()
    files_service.list.return_value = mock_request
    # list next returns a new fake "request" for each page and None at the end of each page (simulating the end of the listing like the Google Drive API behaves in practice)
    files_service.list_next.side_effect = flatten_list(
        [[*[mock_request for _ in range(len(listing) - 1)], None] for listing in listing_results]
    )
    drive_service = MagicMock()
    drive_service.files.return_value = files_service
    mock_build_service.return_value = drive_service

    reader = create_reader()

    found_files = list(reader.get_matching_files([glob], None, MagicMock()))
    assert files_service.list.call_count == len(listing_results)
    assert matched_files == found_files
    assert files_service.list_next.call_count == len(flattened_results)


@pytest.mark.parametrize(
    "file, file_content, mode, expect_export, expected_mime_type, expected_read, expect_raise",
    [
        pytest.param(
            GoogleDriveRemoteFile(
                uri="avro_file", id="abc", mime_type="text/csv", original_mime_type="text/csv", last_modified=datetime.datetime(2021, 1, 1)
            ),
            b"test",
            FileReadMode.READ_BINARY,
            False,
            None,
            b"test",
            False,
            id="Read binary file",
        ),
        pytest.param(
            GoogleDriveRemoteFile(
                uri="test.csv", id="abc", mime_type="text/csv", original_mime_type="text/csv", last_modified=datetime.datetime(2021, 1, 1)
            ),
            b"test",
            FileReadMode.READ,
            False,
            None,
            "test",
            False,
            id="Read text file",
        ),
        pytest.param(
            GoogleDriveRemoteFile(
                uri="abc",
                id="abc",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                original_mime_type="application/vnd.google-apps.document",
                last_modified=datetime.datetime(2021, 1, 1),
            ),
            b"test",
            FileReadMode.READ_BINARY,
            True,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"test",
            False,
            id="Read google doc as binary file with export",
        ),
    ],
)
@patch("source_google_drive.stream_reader.MediaIoBaseDownload")
@patch("source_google_drive.stream_reader.service_account")
@patch("source_google_drive.stream_reader.build")
def test_open_file(
    mock_build_service,
    mock_service_account,
    mock_basedownload,
    file,
    file_content,
    mode,
    expect_export,
    expected_mime_type,
    expected_read,
    expect_raise,
):
    mock_request = MagicMock()
    mock_downloader = MagicMock()

    def mock_next_chunk():
        handle = mock_basedownload.call_args[0][0]
        if handle.tell() > 0:
            return (None, True)
        else:
            handle.write(file_content)
            return (None, False)

    mock_downloader.next_chunk.side_effect = mock_next_chunk

    mock_basedownload.return_value = mock_downloader

    files_service = MagicMock()
    if expect_export:
        files_service.export_media.return_value = mock_request
    else:
        files_service.get_media.return_value = mock_request
    drive_service = MagicMock()
    drive_service.files.return_value = files_service
    mock_build_service.return_value = drive_service

    if expect_raise:
        with pytest.raises(ValueError):
            create_reader().open_file(file, mode, None, MagicMock()).read()
    else:
        assert expected_read == create_reader().open_file(file, mode, None, MagicMock()).read()
        assert mock_downloader.next_chunk.call_count == 2
        if expect_export:
            files_service.export_media.assert_has_calls([call(fileId=file.id, mimeType=expected_mime_type)])
        else:
            files_service.get_media.assert_has_calls([call(fileId=file.id)])
