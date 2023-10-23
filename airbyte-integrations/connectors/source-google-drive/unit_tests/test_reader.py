#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig, Json
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from source_google_drive.spec import ServiceAccountCredentials, SourceGoogleDriveSpec
from source_google_drive.stream_reader import GoogleDriveRemoteFile, SourceGoogleDriveStreamReader


def create_reader(
    config=SourceGoogleDriveSpec(
        folder_url="https://drive.google.com/drive/folders/1Z2Q3",
        streams=[FileBasedStreamConfig(name="test", format=JsonlFormat())],
        credentials=ServiceAccountCredentials(auth_type="Service", service_account_info='{"test": "abc"}'),
    )
):
    reader = SourceGoogleDriveStreamReader()
    reader.config = config

    return reader


@pytest.mark.parametrize(
    "results, expected_files",
    [
        pytest.param(
            [{"files": [{"id": "abc", "mimeType": "text/csv", "name": "test.csv", "modifiedTime": "2021-01-01T00:00:00.000Z"}]}],
            [GoogleDriveRemoteFile(uri="/test.csv", id="abc", mimeType="text/csv", name="test.csv", modifiedTime=datetime(2021, 1, 1))],
            id="Single file",
        )
        # TODO add cases:
        # multiple files
        # multiple pages
        # duplicates
        # subdirectories
        # duplicates in subdirectories
        # duplicate subdirectories
        # not matching the globs (just a basic case is enough)
    ],
)
@patch("source_google_drive.stream_reader.build")
def test_matching_files(mock_build_service, listing_results, matched_files):
    mock_request = MagicMock()
    mock_request.execute.side_effect = [*listing_results, None]
    files_service = MagicMock()
    files_service.list.return_value = mock_request
    files_service.list_next.return_value = mock_request
    drive_service = MagicMock()
    drive_service.files.return_value = files_service
    mock_build_service.return_value = drive_service

    reader = create_reader()

    assert matched_files == reader.get_matching_files(["*"], None, MagicMock())
    assert files_service.list.call_count == 1
    assert files_service.list_next.call_count == len(listing_results) - 1


# TODO add tests for open_file
# get_media with single chunks and multiple chunks
# export_media with sungle chunks and multiple chunks
# binary read
# textual read
