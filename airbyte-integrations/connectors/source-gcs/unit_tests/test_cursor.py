# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from datetime import datetime

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from source_gcs import Cursor


def test_add_file_zip_files(mocked_reader, zip_file, logger):
    unzipped_file = mocked_reader.unzip_files(zip_file, logger)

    cursor = Cursor(stream_config=FileBasedStreamConfig(name="test", globs=["**/*.zip"], format={"filetype": "csv"}))
    cursor.add_file(unzipped_file)

    saved_history_cursor = datetime.strptime(
        cursor._file_to_datetime_history[unzipped_file.displayed_uri],
        cursor.DATE_TIME_FORMAT
    )

    assert saved_history_cursor == zip_file.last_modified
