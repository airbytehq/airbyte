#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import os
import shutil
from pathlib import Path
from typing import Any, Dict
import pytest
from airbyte_cdk import AirbyteLogger
from source_s3.source import SourceS3
from unit_tests.abstract_test_parser import memory_limit
from unit_tests.test_csv_parser import generate_big_file

from .conftest import TMP_FOLDER

HERE = Path(__file__).resolve().parent


class TestIntegrationCsvFiles:
    logger = AirbyteLogger()

    @memory_limit(150)  # max used memory should be less than 150Mb
    def read_source(self, credentials: Dict[str, Any], catalog: Dict[str, Any]) -> int:
        read_count = 0
        for msg in SourceS3().read(logger=self.logger, config=credentials, catalog=catalog):
            if msg.record:
                read_count += 1
        return read_count

    @pytest.mark.order(1)
    def test_big_file(self, minio_credentials: Dict[str, Any]) -> None:
        """tests a big csv file (>= 1.0G records)"""
        # generates a big CSV files separately
        big_file_folder = os.path.join(TMP_FOLDER, "minio_data", "test-bucket", "big_files")
        shutil.rmtree(big_file_folder, ignore_errors=True)
        os.makedirs(big_file_folder)
        filepath = os.path.join(big_file_folder, "file.csv")

        # please change this value if you need to test another file size
        future_file_size = 0.5  # in gigabytes
        _, file_size = generate_big_file(filepath, future_file_size, 500)
        expected_count = sum(1 for _ in open(filepath)) - 1
        self.logger.info(f"generated file {filepath} with size {file_size}Gb, lines: {expected_count}")

        minio_credentials["path_pattern"] = "big_files/*.csv"
        minio_credentials["format"]["block_size"] = 5 * 1024 ** 2
        source = SourceS3()
        catalog = source.read_catalog(HERE / "configured_catalog.json")

        assert self.read_source(minio_credentials, catalog) == expected_count
