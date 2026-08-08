#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import csv
from io import StringIO
from typing import Dict, List, Optional

from psycopg2 import sql
from psycopg2.extras import Json

from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier, format_exception
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_opengauss_datavec.config import OpenGaussDataVecIndexingModel
from destination_opengauss_datavec.connection import OpenGaussSslConnectionOptions, get_connection
from destination_opengauss_datavec.row_builder import RowBuilder
from destination_opengauss_datavec.schema import MetadataColumn, SchemaBuilder, StreamDestination, normalize_identifier


COPY_NULL_VALUE = "\x1d"


class OpenGaussDataVecIndexer(Indexer):
    config: OpenGaussDataVecIndexingModel

    def __init__(
        self,
        config: OpenGaussDataVecIndexingModel,
        embedding_dimensions: int,
        processing_config: ProcessingConfigModel,
        omit_raw_text: bool,
    ):
        """Keep config and prepared stream targets needed by Writer callbacks."""
        super().__init__(config)
        self.embedding_dimensions = embedding_dimensions
        self.omit_raw_text = omit_raw_text
        self.schema_builder = SchemaBuilder(processing_config, config.default_schema)
        self.row_builder = RowBuilder(omit_raw_text)
        self.ssl_connection_options = OpenGaussSslConnectionOptions(config)
        self.streams: Dict[str, StreamDestination] = {}
        self._conn = None

    def _get_connection(self):
        """Return the shared connection, reconnecting if it was lost."""
        if self._conn is None or self._conn.closed:
            self._conn = get_connection(self.config, self.ssl_connection_options)
        return self._conn

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        """Prepare schema and stream tables before records start flowing."""
        with self._get_connection().cursor() as cursor:
            for configured_stream in catalog.streams:
                destination = self.schema_builder.create_stream_destination(configured_stream)
                self.streams[create_stream_identifier(configured_stream.stream)] = destination
                self._create_schema(cursor, destination.schema_name)

                if destination.mode == DestinationSyncMode.overwrite:
                    self._drop_table(cursor, destination.schema_name, destination.write_table_name)
                    self._create_table(cursor, destination.schema_name, destination.write_table_name, destination.metadata_columns)
                else:
                    self._create_table(cursor, destination.schema_name, destination.table_name, destination.metadata_columns)
                    if destination.mode == DestinationSyncMode.append_dedup:
                        self._create_document_id_index(cursor, destination.schema_name, destination.table_name)
        self._get_connection().commit()

    def index(self, document_chunks: List[Chunk], namespace: Optional[str], stream: str) -> None:
        """Bulk load embedded chunks into the stream's final or staging table."""
        if not document_chunks:
            return

        stream_identifier = str(stream if namespace is None else f"{namespace}_{stream}")
        destination = self.streams[stream_identifier]
        copy_columns = self.row_builder.copy_columns(destination.metadata_columns)
        rows = self.row_builder.create_rows(document_chunks, destination.metadata_columns)

        with self._get_connection().cursor() as cursor:
            copy_sql = sql.SQL("COPY {}.{} ({}) FROM STDIN WITH (FORMAT CSV, NULL {})").format(
                sql.Identifier(destination.schema_name),
                sql.Identifier(destination.write_table_name),
                sql.SQL(", ").join(sql.Identifier(column) for column in copy_columns),
                sql.Literal(COPY_NULL_VALUE),
            )
            cursor.copy_expert(copy_sql.as_string(cursor), rows_to_csv(rows))
        self._get_connection().commit()

    def delete(self, delete_ids: List[str], namespace: Optional[str], stream: str) -> None:
        """Delete old chunks for append_dedup streams by document_id."""
        if not delete_ids:
            return

        stream_identifier = str(stream if namespace is None else f"{namespace}_{stream}")
        destination = self.streams[stream_identifier]
        if destination.mode != DestinationSyncMode.append_dedup:
            return

        with self._get_connection().cursor() as cursor:
            cursor.execute(
                sql.SQL("DELETE FROM {}.{} WHERE document_id = ANY(%s)").format(
                    sql.Identifier(destination.schema_name),
                    sql.Identifier(destination.table_name),
                ),
                (delete_ids,),
            )
        self._get_connection().commit()

    def post_sync(self):
        """Promote overwrite staging tables and close the shared connection."""
        try:
            overwrite_streams = [destination for destination in self.streams.values() if destination.mode == DestinationSyncMode.overwrite]
            if overwrite_streams:
                with self._get_connection().cursor() as cursor:
                    for destination in overwrite_streams:
                        self._drop_table(cursor, destination.schema_name, destination.table_name)
                        cursor.execute(
                            sql.SQL("ALTER TABLE {}.{} RENAME TO {}").format(
                                sql.Identifier(destination.schema_name),
                                sql.Identifier(destination.write_table_name),
                                sql.Identifier(destination.table_name),
                            )
                        )
                self._get_connection().commit()
        finally:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
        return []

    def check(self) -> Optional[str]:
        """Validate that the configured database can be reached."""
        conn = None
        try:
            conn = get_connection(self.config, self.ssl_connection_options)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            return format_exception(e)
        finally:
            if conn is not None:
                conn.close()
        return None

    def _create_schema(self, cursor, schema_name: str) -> None:
        """Create a destination schema if it does not already exist."""
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))

    def _create_table(self, cursor, schema_name: str, table_name: str, metadata_columns: List[MetadataColumn]) -> None:
        """Create the stream table and add optional columns missing from existing tables."""
        columns = [
            sql.SQL("{} text").format(sql.Identifier("document_id")),
            sql.SQL("{} text").format(sql.Identifier("chunk_id")),
        ]
        if not self.omit_raw_text:
            columns.append(sql.SQL("{} text").format(sql.Identifier("content")))
        columns.append(sql.SQL("{} vector({})").format(sql.Identifier("embedding"), sql.SQL(str(self.embedding_dimensions))))
        columns.extend(sql.SQL("{} {}").format(sql.Identifier(column.column_name), sql.SQL(column.sql_type)) for column in metadata_columns)
        columns.extend(
            [
                sql.SQL("{} timestamp with time zone").format(sql.Identifier("_airbyte_extracted_at")),
                sql.SQL("{} jsonb").format(sql.Identifier("_airbyte_meta")),
            ]
        )

        cursor.execute(
            sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({})").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.SQL(", ").join(columns),
            )
        )

        # Append streams may already have tables from earlier syncs, so add newly configured optional columns in place.
        if not self.omit_raw_text:
            self._add_column_if_missing(cursor, schema_name, table_name, "content", "text")
        for column in metadata_columns:
            self._add_column_if_missing(cursor, schema_name, table_name, column.column_name, column.sql_type)

    def _drop_table(self, cursor, schema_name: str, table_name: str) -> None:
        """Drop a destination table if it already exists."""
        cursor.execute(sql.SQL("DROP TABLE IF EXISTS {}.{}").format(sql.Identifier(schema_name), sql.Identifier(table_name)))

    def _create_document_id_index(self, cursor, schema_name: str, table_name: str) -> None:
        """Create the document_id index used by append_dedup deletes."""
        index_name = normalize_identifier(f"{table_name}_document_id_idx")
        cursor.execute(
            sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} ({})").format(
                sql.Identifier(index_name),
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.Identifier("document_id"),
            )
        )

    def _add_column_if_missing(self, cursor, schema_name: str, table_name: str, column_name: str, column_type: str) -> None:
        """Add one optional column to an existing table."""
        cursor.execute(
            sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS {} {}").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.Identifier(column_name),
                sql.SQL(column_type),
            )
        )


def rows_to_csv(rows) -> StringIO:
    """Serialize COPY rows in CSV format for psycopg2 copy_expert."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    for row in rows:
        writer.writerow([copy_value(value) for value in row])
    buffer.seek(0)
    return buffer


def copy_value(value):
    if value is None:
        return COPY_NULL_VALUE
    if isinstance(value, Json):
        return value.dumps(value.adapted)
    return value
