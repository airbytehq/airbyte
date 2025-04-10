# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import csv
import os
from pathlib import Path
from unittest import TestCase

from destination_cobra.processor.batch import CsvSizeEstimator

from airbyte_cdk import AirbyteRecordMessage


class TestCsvSizeEstimator(TestCase):
    _BUFFER_IN_BYTES = 10

    def setUp(self) -> None:
        self._size_estimator = CsvSizeEstimator()

    def test_when_get_size_then_return_size_on_disk_within_boundaries(self) -> None:
        filepath = str(Path(__file__).parent / "data.csv")
        with open(filepath) as fh:
            for row in csv.DictReader(fh):
                self._size_estimator.add(
                    AirbyteRecordMessage(
                        stream="test",
                        data=row,
                        emitted_at=0,
                    )
                )

        expected_size = os.path.getsize(filepath)
        assert expected_size + self._BUFFER_IN_BYTES >= self._size_estimator.get_size() >= expected_size - self._BUFFER_IN_BYTES
