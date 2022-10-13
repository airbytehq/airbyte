#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_sqlite import DestinationSqlite


def test_get_destination_path():
    user_input = "sqlite.db"
    expected = "/local/sqlite.db"

    out = DestinationSqlite._get_destination_path(user_input)
    assert out == expected

    user_input = "/local/sqlite.db"
    expected = "/local/sqlite.db"

    out = DestinationSqlite._get_destination_path(user_input)
    assert out == expected

    invalid_input = "/sqlite.db"
    with pytest.raises(ValueError):
        _ = DestinationSqlite._get_destination_path(invalid_input)
