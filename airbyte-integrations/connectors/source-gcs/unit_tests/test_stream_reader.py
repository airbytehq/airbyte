# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles
from source_gcs import Config


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

def test_unzip_files(mocked_reader, zip_file, logger, caplog):
    unzipped_file = mocked_reader.unzip_files(zip_file, logger)

    assert unzipped_file
    assert unzipped_file.displayed_uri
    assert unzipped_file.uri
    assert "Picking up first file test.csv from zip archive" in caplog.text

