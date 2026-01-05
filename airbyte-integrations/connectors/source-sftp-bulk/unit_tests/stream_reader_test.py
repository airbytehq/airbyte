# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
import pytest
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SFTPBulkUploadableRemoteFile, SourceSFTPBulkStreamReader

from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError


logger = logging.Logger("")


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_files_read_and_filter_by_date():
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)
    files_on_server = [
        [
            MagicMock(filename="sample_file_1.csv", st_mode=180, st_mtime=1704067200),
            MagicMock(filename="sample_file_2.csv", st_mode=180, st_mtime=1704060200),
        ]
    ]
    fake_client.listdir_iter = MagicMock(side_effect=files_on_server)
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert len(files) == 1
        assert files[0].uri == "//sample_file_1.csv"
        assert files[0].last_modified == datetime.datetime(2024, 1, 1, 0, 0)


def test_upload_file_size_error():
    reader = SourceSFTPBulkStreamReader()
    config = SourceSFTPBulkSpec(
        host="localhost",
        username="username",
        credentials={"auth_type": "password", "password": "password"},
        port=123,
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )
    reader.config = config

    class SizeOverWriteSFTPBulkUploadableRemoteFile(SFTPBulkUploadableRemoteFile):
        @property
        def size(self) -> int:
            return SourceSFTPBulkStreamReader.FILE_SIZE_LIMIT + 1

    file = SizeOverWriteSFTPBulkUploadableRemoteFile(
        uri="//sample_file_1.csv",
        last_modified=datetime.datetime(2024, 1, 1, 0, 0),
        config=config,
        sftp_client=MagicMock(),
        logger=logger,
    )
    with pytest.raises(FileSizeLimitError) as err:
        reader.upload(file, "/test", MagicMock())
    assert str(err.value) == "File size exceeds the 1.5 GB limit. File URI: //sample_file_1.csv"
