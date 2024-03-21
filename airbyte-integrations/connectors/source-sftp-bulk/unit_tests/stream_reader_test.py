# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import datetime
import logging
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader

logger = logging.Logger("")


@freezegun.freeze_time("2024-01-01T00:00:00")
def test_stream_reader():
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)
    files = [[MagicMock(filename="sample_file_1.csv", st_mode=180, st_mtime=1704067200)]]
    fake_client.listdir_attr = MagicMock(side_effect=files)
    # patch("paramiko.SFTPClient.listdir_attr", side_effect=[1,2,3]),
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(host="localhost", username="username", password="password", port=123, streams=[])
        reader.config = config
        file = next(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert file.uri == "//sample_file_1.csv"
        assert file.last_modified == datetime.datetime(2024, 1, 1, 0, 0)
