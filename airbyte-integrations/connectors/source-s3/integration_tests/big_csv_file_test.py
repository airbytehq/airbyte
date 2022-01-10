#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import os
from pathlib import Path
from typing import Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from source_s3.source import SourceS3
from unit_tests.abstract_test_parser import memory_limit
from unit_tests.test_csv_parser import generate_big_file

from .acceptance import TMP_FOLDER

HERE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def credentials() -> Mapping:
    filename = HERE / "config_minio.json"
    with open(filename) as f:
        return json.load(f)


class TestIntegrationCsvFiles:
    logger = AirbyteLogger()

    @memory_limit(150)  # max used memory should be less than 20Mb
    def read_source(self, credentials, catalog):
        read_count = 0
        for msg in SourceS3().read(logger=self.logger, config=credentials, catalog=catalog):
            if msg.record:
                read_count += 1
        return read_count

    @pytest.mark.order(1)
    def test_big_file(self, credentials):
        """tests a big csv file (>= 1.0G records)"""
        # generates a big CSV files separately
        big_file_folder = os.path.join(TMP_FOLDER, "minio_data", "test-bucket", "big_files")
        os.makedirs(big_file_folder)
        filepath = os.path.join(big_file_folder, "file.csv")

        # please change this value if you need to test another file size
        future_file_size = 0.5  # in gigabytes
        _, file_size = generate_big_file(filepath, future_file_size, 500)
        expected_count = sum(1 for _ in open(filepath)) - 1
        self.logger.info(f"generated file {filepath} with size {file_size}Gb, lines: {expected_count}")

        credentials["path_pattern"] = "big_files/*.csv"
        credentials["format"]["block_size"] = 5 * 1024 ** 2
        source = SourceS3()
        catalog = source.read_catalog(HERE / "configured_catalog.json")

        assert self.read_source(credentials, catalog) == expected_count
