#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_duckdb import DestinationDuckdb


def test_read_invalid_path():

    invalid_input = "/test.duckdb"
    with pytest.raises(ValueError):
        _ = DestinationDuckdb._get_destination_path(invalid_input)

    assert True
