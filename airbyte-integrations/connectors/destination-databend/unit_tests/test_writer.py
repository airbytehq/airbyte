#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Union
from unittest.mock import MagicMock

from destination_databend.writer import DatabendSQLWriter
from pytest import fixture, mark


@fixture
def client() -> MagicMock:
    return MagicMock()


@fixture
def sql_writer(client: MagicMock) -> DatabendSQLWriter:
    return DatabendSQLWriter(client)


def test_sql_default(sql_writer: DatabendSQLWriter) -> None:
    assert len(sql_writer._buffer) == 0
    assert sql_writer.flush_interval == 1000


@mark.parametrize("writer", ["sql_writer"])
def test_sql_create(client: MagicMock, writer: Union[DatabendSQLWriter], request: Any) -> None:
    writer = request.getfixturevalue(writer)
    writer.create_raw_table("dummy")


def test_data_buffering(sql_writer: DatabendSQLWriter) -> None:
    sql_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    sql_writer._buffer["dummy"][0] == ("id1", 20200101, '{"key": "value"}')
    assert len(sql_writer._buffer["dummy"]) == 1
    assert len(sql_writer._buffer.keys()) == 1
    sql_writer.queue_write_data("dummy", "id2", 20200102, '{"key2": "value2"}')
    sql_writer._buffer["dummy"][0] == ("id2", 20200102, '{"key2": "value2"}')
    assert len(sql_writer._buffer["dummy"]) == 2
    assert len(sql_writer._buffer.keys()) == 1
    sql_writer.queue_write_data("dummy2", "id3", 20200103, '{"key3": "value3"}')
    sql_writer._buffer["dummy"][0] == ("id3", 20200103, '{"key3": "value3"}')
    assert len(sql_writer._buffer["dummy"]) == 2
    assert len(sql_writer._buffer["dummy2"]) == 1
    assert len(sql_writer._buffer.keys()) == 2
