#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from json import load
from unittest.mock import MagicMock

import pytest
from source_firebolt.source import establish_connection

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is sets up external resources that acceptance test might require."""
    with open("secrets/config.json") as f:
        config = load(f)
    with establish_connection(config, MagicMock()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE DIMENSION TABLE airbyte_acceptance_table (column1 STRING, column2 INT, column3 DATETIME, column4 DOUBLE NULL, column5 ARRAY(INT NULL))"
            )
            cursor.execute(
                "INSERT INTO airbyte_acceptance_table VALUES ('my_value',221,'2021-01-01 20:10:22.448',1.214, [1,2,3]), ('my_value2',222,'2021-01-02 22:10:22.448',null,[1,2,null])"
            )
            yield connection
            cursor.execute("DROP TABLE airbyte_acceptance_table")
