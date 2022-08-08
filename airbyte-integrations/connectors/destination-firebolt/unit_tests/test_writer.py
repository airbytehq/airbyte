#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Union
from unittest.mock import ANY, MagicMock, call, patch

from destination_firebolt.writer import FireboltS3Writer, FireboltSQLWriter
from pytest import fixture, mark


@fixture
def connection() -> MagicMock:
    return MagicMock()


@fixture
def sql_writer(connection: MagicMock) -> FireboltSQLWriter:
    return FireboltSQLWriter(connection)


@fixture
@patch("destination_firebolt.writer.time", MagicMock(return_value=111))
@patch("destination_firebolt.writer.uuid4", MagicMock(return_value="dummy-uuid"))
def s3_writer(connection: MagicMock) -> FireboltS3Writer:
    # Make sure S3FileSystem mock is reset each time
    with patch("destination_firebolt.writer.fs.S3FileSystem", MagicMock()):
        return FireboltS3Writer(connection, "dummy_bucket", "access_key", "secret_key", "us-east-1")


def test_sql_default(sql_writer: FireboltSQLWriter) -> None:
    assert len(sql_writer._buffer) == 0
    assert sql_writer.flush_interval == 1000


@mark.parametrize("writer", ["sql_writer", "s3_writer"])
def test_sql_create(connection: MagicMock, writer: Union[FireboltSQLWriter, FireboltS3Writer], request: Any) -> None:
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
    connection.cursor.return_value.execute.assert_called_once_with(expected_query)


def test_data_buffering(sql_writer: FireboltSQLWriter) -> None:
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


def test_data_auto_flush_one_table(connection: MagicMock, sql_writer: FireboltSQLWriter) -> None:
    sql_writer.flush_interval = 2
    sql_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    connection.cursor.return_value.executemany.assert_not_called()
    assert sql_writer._values == 1
    sql_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    connection.cursor.return_value.executemany.assert_called_once()
    assert len(sql_writer._buffer.keys()) == 0
    assert sql_writer._values == 0
    sql_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    assert len(sql_writer._buffer.keys()) == 1


def test_data_auto_flush_multi_tables(connection: MagicMock, sql_writer: FireboltSQLWriter) -> None:
    sql_writer.flush_interval = 2
    sql_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    connection.cursor.return_value.executemany.assert_not_called()
    assert sql_writer._values == 1
    sql_writer.queue_write_data("dummy2", "id1", 20200101, '{"key": "value"}')
    assert len(connection.cursor.return_value.executemany.mock_calls) == 2
    assert len(sql_writer._buffer.keys()) == 0
    assert sql_writer._values == 0


def test_s3_default(s3_writer: FireboltS3Writer) -> None:
    assert s3_writer.flush_interval == 100000
    assert s3_writer._values == 0
    assert len(s3_writer._buffer.keys()) == 0


def test_s3_delete_tables(connection: MagicMock, s3_writer: FireboltS3Writer) -> None:
    expected_sql = "DROP TABLE IF EXISTS _airbyte_raw_dummy"
    s3_writer.delete_table("dummy")
    connection.cursor.return_value.execute.assert_called_once_with(expected_sql)


@patch("pyarrow.parquet.write_to_dataset")
def test_s3_data_auto_flush_one_table(mock_write: MagicMock, s3_writer: FireboltS3Writer) -> None:
    s3_writer.flush_interval = 2
    s3_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    mock_write.assert_not_called()
    assert s3_writer._values == 1
    s3_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    mock_write.assert_called_once_with(table=ANY, root_path="dummy_bucket/airbyte_output/111_dummy-uuid/dummy", filesystem=s3_writer.fs)
    assert len(s3_writer._buffer.keys()) == 0
    assert s3_writer._values == 0
    assert s3_writer._updated_tables == set(["dummy"])
    mock_write.reset_mock()
    s3_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    mock_write.assert_not_called()
    assert len(s3_writer._buffer.keys()) == 1
    assert s3_writer._updated_tables == set(["dummy"])


@patch("pyarrow.parquet.write_to_dataset")
def test_s3_data_auto_flush_multi_tables(mock_write: MagicMock, s3_writer: FireboltS3Writer) -> None:
    s3_writer.flush_interval = 2
    s3_writer.queue_write_data("dummy", "id1", 20200101, '{"key": "value"}')
    mock_write.assert_not_called()
    assert s3_writer._values == 1
    s3_writer.queue_write_data("dummy2", "id1", 20200101, '{"key": "value"}')
    assert mock_write.mock_calls == [
        call(table=ANY, root_path="dummy_bucket/airbyte_output/111_dummy-uuid/dummy", filesystem=s3_writer.fs),
        call(table=ANY, root_path="dummy_bucket/airbyte_output/111_dummy-uuid/dummy2", filesystem=s3_writer.fs),
    ]
    assert len(s3_writer._buffer.keys()) == 0
    assert s3_writer._values == 0
    assert s3_writer._updated_tables == set(["dummy", "dummy2"])


def test_s3_final_flush(connection: MagicMock, s3_writer: FireboltS3Writer) -> None:
    s3_writer._updated_tables = set(["dummy", "dummy2"])
    s3_writer.flush()
    assert len(connection.cursor.return_value.execute.mock_calls) == 8
    expected_url1 = "s3://dummy_bucket/airbyte_output/111_dummy-uuid/dummy"
    expected_url2 = "s3://dummy_bucket/airbyte_output/111_dummy-uuid/dummy2"
    connection.cursor.return_value.execute.assert_any_call(ANY, parameters=(expected_url1, "access_key", "secret_key"))
    connection.cursor.return_value.execute.assert_any_call(ANY, parameters=(expected_url2, "access_key", "secret_key"))
    expected_query1 = "INSERT INTO _airbyte_raw_dummy SELECT * FROM ex_airbyte_raw_dummy"
    expected_query2 = "INSERT INTO _airbyte_raw_dummy2 SELECT * FROM ex_airbyte_raw_dummy2"
    connection.cursor.return_value.execute.assert_any_call(expected_query1)
    connection.cursor.return_value.execute.assert_any_call(expected_query2)


def test_s3_cleanup(connection: MagicMock, s3_writer: FireboltS3Writer) -> None:
    expected_sql = "DROP TABLE IF EXISTS ex_airbyte_raw_my_table"
    bucket_path = "dummy_bucket/airbyte_output/111_dummy-uuid/my_table"
    s3_writer.cleanup("my_table")
    connection.cursor.return_value.execute.assert_called_once_with(expected_sql)
    s3_writer.fs.delete_dir_contents.assert_called_once_with(bucket_path)
