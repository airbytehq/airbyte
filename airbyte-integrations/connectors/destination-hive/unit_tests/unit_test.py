from typing import Any, Union
from unittest.mock import ANY, MagicMock, call, patch

from destination_hive.writer import HiveSQLWriter
from pytest import fixture, mark

from logging import getLogger


@fixture
def client() -> MagicMock:
    return MagicMock()


@fixture
def sql_writer(client: MagicMock) -> HiveSQLWriter:
    return HiveSQLWriter(client, {}, getLogger('airbyte'))


def test_sql_default(sql_writer: HiveSQLWriter) -> None:
    assert len(sql_writer._buffer) == 0
    assert sql_writer.flush_interval == 1000


@mark.parametrize("writer", ["sql_writer"])
def test_sql_create(client: MagicMock, writer: Union[HiveSQLWriter], request: Any) -> None:
    writer = request.getfixturevalue(writer)
    expected_query = """
        CREATE FACT TABLE IF NOT EXISTS _airbyte_raw_dummy (
            _airbyte_ab_id TEXT,
            _airbyte_emitted_at TIMESTAMP,
            _airbyte_data TEXT
        )
        PRIMARY INDEX _airbyte_ab_id
        """
    writer.create_raw_table("dummy")


def test_data_buffering(sql_writer: HiveSQLWriter) -> None:
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

