# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

import duckdb
from airbyte_protocol.models import AirbyteMessage  # type: ignore
from live_tests.commons.backends.file_backend import FileBackend


class DuckDbBackend(FileBackend):
    SAMPLE_SIZE = -1

    def __init__(
        self,
        output_directory: Path,
        duckdb_path: Path,
        schema: Optional[Iterable[str]] = None,
    ):
        super().__init__(output_directory)
        self.duckdb_path = duckdb_path
        self.schema = schema

    @property
    def jsonl_files_to_insert(self) -> Iterable[Path]:
        return [
            self.jsonl_catalogs_path,
            self.jsonl_connection_status_path,
            self.jsonl_specs_path,
            self.jsonl_states_path,
            self.jsonl_traces_path,
            self.jsonl_logs_path,
            self.jsonl_controls_path,
            self.jsonl_records_path,
        ]

    @staticmethod
    def sanitize_table_name(table_name: str) -> str:
        sanitized = table_name.replace(" ", "_")
        sanitized = re.sub(r"[^\w\s]", "", sanitized)
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        return sanitized

    def write(self, airbyte_messages: Iterable[AirbyteMessage]) -> None:
        # Use the FileBackend to write the messages to disk as jsonl files
        super().write(airbyte_messages)
        duck_db_conn = duckdb.connect(str(self.duckdb_path))

        if self.schema:
            sanitized_schema_name = "_".join([self.sanitize_table_name(s) for s in self.schema])
            duck_db_conn.sql(f"CREATE SCHEMA IF NOT EXISTS {sanitized_schema_name}")
            duck_db_conn.sql(f"USE {sanitized_schema_name}")
            logging.info(f"Using schema {sanitized_schema_name}")

        for json_file in self.jsonl_files_to_insert:
            if json_file.exists():
                table_name = self.sanitize_table_name(json_file.stem)
                logging.info(f"Creating table {table_name} from {json_file} in schema {sanitized_schema_name}")
                duck_db_conn.sql(
                    f"CREATE TABLE {table_name} AS SELECT * FROM read_json_auto('{json_file}', sample_size = {self.SAMPLE_SIZE}, format = 'newline_delimited')"
                )
                logging.info(f"Table {table_name} created in schema {sanitized_schema_name}")

        for json_file in self.record_per_stream_paths_data_only.values():
            if json_file.exists():
                table_name = self.sanitize_table_name(f"records_{json_file.stem}")
                logging.info(
                    f"Creating table {table_name} from {json_file} in schema {sanitized_schema_name} to store stream records with the data field only"
                )
                duck_db_conn.sql(
                    f"CREATE TABLE {self.sanitize_table_name(table_name)} AS SELECT * FROM read_json_auto('{json_file}', sample_size = {self.SAMPLE_SIZE}, format = 'newline_delimited')"
                )
                logging.info(f"Table {table_name} created in schema {sanitized_schema_name}")
        duck_db_conn.close()
