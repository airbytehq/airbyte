# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Optional

from base_test import BaseTest
from bingads.v13.bulk.bulk_service_manager import BulkServiceManager


class TestBulkStream(BaseTest):
    @property
    def service_manager(self) -> BulkServiceManager:
        return BulkServiceManager

    def _download_file(self, file: Optional[str] = None) -> Path:
        """
        Returns path to temporary file of downloaded data that will be use in read.
        Base file should be named as {file_name}.cvs in resource/response folder.
        """
        if file:
            path_to_tmp_file = Path(__file__).parent.parent / f"resource/response/{file}_tmp.csv"
            path_to_file_base = Path(__file__).parent.parent / f"resource/response/{file}.csv"
            with open(path_to_file_base, "r") as f1, open(path_to_tmp_file, "w") as f2:
                for line in f1:
                    f2.write(line)
            return path_to_tmp_file
        return Path(__file__).parent.parent / "resource/response/non-existing-file.csv"
