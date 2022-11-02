#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_duckdb import DestinationDuckdb


def test_example_method():

    invalid_input = "/test.ducdb"
    with pytest.raises(ValueError):
        _ = DestinationDuckdb._get_destination_path(invalid_input)

    assert True
