# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Iterable

import duckdb
from airbyte_protocol.models import AirbyteMessage  # type: ignore
from live_tests.commons.backends.file_backend import FileBackend


class DuckDbBackend(FileBackend):
    DUCK_DB_FILE_NAME = "duck.db"

    def write(self, airbyte_messages: Iterable[AirbyteMessage]) -> None:
        # Use the FileBackend to write the messages to disk as jsonl files
        super().write(airbyte_messages)
        duck_db_conn = duckdb.connect(f"{self._output_directory}/{self.DUCK_DB_FILE_NAME}")
        for jsonl_file in self.jsonl_files:
            if jsonl_file.exists():
                duck_db_conn.sql(f"CREATE TABLE {jsonl_file.stem} AS SELECT * FROM read_json_auto('{jsonl_file}')")
        duck_db_conn.close()
