#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.sources.streams.files import FileInfo

DUMMY_STRING = "file_key"
FILE_INFO_A = FileInfo(DUMMY_STRING, 10485760, pendulum.now())
FILE_INFO_B = FileInfo(DUMMY_STRING, 10, pendulum.now() - pendulum.duration(days=1))
FILE_INFO_C = FileInfo("different_key", 10, pendulum.now() - pendulum.duration(days=1))


class TestFileInfo:
    def test_size_in_megabytes(self):
        assert FILE_INFO_A.size_in_megabytes == 10

    def test_equality(self):
        assert FILE_INFO_A == FILE_INFO_A
        assert FILE_INFO_A != FILE_INFO_B
        assert FILE_INFO_A != FILE_INFO_C
        assert FILE_INFO_A != DUMMY_STRING

    def test_comparison(self):
        assert FILE_INFO_B < FILE_INFO_A
        assert FILE_INFO_A > FILE_INFO_C
        with pytest.raises(TypeError):
            assert FILE_INFO_A < DUMMY_STRING
