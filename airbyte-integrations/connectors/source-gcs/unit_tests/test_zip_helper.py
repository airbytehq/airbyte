# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import tempfile

from source_gcs.zip_helper import ZipHelper


def test_get_gcs_remote_files(mocked_blob, zip_file, caplog):
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        files = list(ZipHelper(mocked_blob, zip_file, tmp_dir_path).get_gcs_remote_files())
    assert len(files) == 1
    assert "Picking up file test.csv from zip archive" in caplog.text
