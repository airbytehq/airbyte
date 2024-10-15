# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime

import pytest
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_gcs import Config, SourceGCSStreamReader


def test_get_matching_files_with_no_prefix(logger, mocked_reader):
    mocked_reader._config = Config(
        service_account='{"type": "service_account"}',
        bucket="test_bucket",
        streams=[],
    )
    globs = ["**/*.csv"]

    with pytest.raises(ErrorListingFiles):
        list(mocked_reader.get_matching_files(globs, None, logger))

    # Assert there is a valid prefix:glob pair, so for loop enters execution.
    assert mocked_reader._gcs_client.get_bucket.called == 1


def test_open_file_with_compression(logger):
    reader = SourceGCSStreamReader()
    reader._config = Config(
        service_account='{"type": "service_account"}',
        bucket="test_bucket",
        streams=[],
    )
    file = RemoteFile(uri="http://some.uri/file.gz?query=param", last_modified=datetime.datetime.now())
    file.mime_type = "file.gz"

    with pytest.raises(OSError):
        reader.open_file(file, FileReadMode.READ_BINARY, None, logger)


def test_open_file_without_compression(remote_file, logger):
    reader = SourceGCSStreamReader()
    reader._config = Config(
        service_account='{"type": "service_account"}',
        bucket="test_bucket",
        streams=[],
    )

    with pytest.raises(OSError):
        reader.open_file(remote_file, FileReadMode.READ, None, logger)
