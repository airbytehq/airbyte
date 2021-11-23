#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from unit_tests.abstract_test_parser import memory_limit


class TestIntegrationCsvFiles:

    @memory_limit(512)
    @pytest.mark.order(1)
    def test_big_file(self):
        """tests a big csv file (>= 1.5G records)"""
        assert False


