#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from importlib.metadata import version

import pandas as pd
from packaging.version import Version
from sqlalchemy import create_engine
from sqlalchemy.sql.elements import TextClause

from destination_snowflake_cortex.cortex_processor import SnowflakeCortexSqlProcessor


def test_patched_langchain_core_and_vector_db_imports_are_available():
    assert Version(version("langchain-core")) >= Version("1.2.5")

    from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
    from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
    from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
    from airbyte_cdk.destinations.vector_db_based.writer import Writer

    assert all((DocumentProcessor, Embedder, Indexer, Writer, create_from_config))


def test_pandas_to_sql_accepts_sqlite_uri():
    pd.DataFrame({"value": [1]}).to_sql("table", "sqlite://", if_exists="append", index=False)


def test_snowflake_cortex_emulated_merge_replaces_rows():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE final_table (document_id TEXT, chunk_id TEXT, value TEXT)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE temp_table (document_id TEXT, chunk_id TEXT, value TEXT)"
        )
        connection.exec_driver_sql(
            "INSERT INTO final_table VALUES ('document-1', 'old-chunk', 'old')"
        )
        connection.exec_driver_sql(
            "INSERT INTO temp_table VALUES ('document-1', 'new-chunk', 'new')"
        )

    processor = SnowflakeCortexSqlProcessor.__new__(SnowflakeCortexSqlProcessor)
    processor._get_sql_column_definitions = lambda stream_name: {
        "document_id": object(),
        "chunk_id": object(),
        "value": object(),
    }
    processor.get_sql_connection = engine.begin

    processor._emulated_merge_temp_table_to_final_table(
        stream_name="stream",
        temp_table_name="temp_table",
        final_table_name="final_table",
    )

    with engine.connect() as connection:
        rows = connection.exec_driver_sql(
            "SELECT document_id, chunk_id, value FROM final_table"
        ).fetchall()
    assert rows == [("document-1", "new-chunk", "new")]


def test_snowflake_cortex_connection_settings_use_executable_sql():
    statements = []

    class ConnectionStub:
        def execute(self, statement):
            statements.append(statement)

    processor = SnowflakeCortexSqlProcessor.__new__(SnowflakeCortexSqlProcessor)
    processor._init_connection_settings(ConnectionStub())

    assert len(statements) == 1
    assert isinstance(statements[0], TextClause)
