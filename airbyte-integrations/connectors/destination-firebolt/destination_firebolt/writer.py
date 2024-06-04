#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from collections import defaultdict
from datetime import datetime
from time import time
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
from firebolt.db import Connection
from pyarrow import fs


class FireboltWriter:
    """
    Base class for shared writer logic.
    """

    flush_interval = 1000

    def __init__(self, connection: Connection) -> None:
        """
        :param connection: Firebolt SDK connection class with established connection
            to the databse.
        """
        self.connection = connection
        self._buffer = defaultdict(list)
        self._values = 0

    def delete_table(self, name: str) -> None:
        """
        Delete the resulting table.
        Primarily used in Overwrite strategy to clean up previous data.

        :param name: table name to delete.
        """
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS _airbyte_raw_{name}")

    def create_raw_table(self, name: str):
        """
        Create the resulting _airbyte_raw table.

        :param name: table name to create.
        """
        query = f"""
        CREATE FACT TABLE IF NOT EXISTS _airbyte_raw_{name} (
            _airbyte_ab_id TEXT,
            _airbyte_emitted_at TIMESTAMP,
            _airbyte_data TEXT
        )
        PRIMARY INDEX _airbyte_ab_id
        """
        cursor = self.connection.cursor()
        cursor.execute(query)

    def queue_write_data(self, stream_name: str, id: str, time: datetime, record: str) -> None:
        """
        Queue up data in a buffer in memory before writing to the database.
        When flush_interval is reached data is persisted.

        :param stream_name: name of the stream for which the data corresponds.
        :param id: unique identifier of this data row.
        :param time: time of writing.
        :param record: string representation of the json data payload.
        """
        self._buffer[stream_name].append((id, time, record))
        self._values += 1
        if self._values == self.flush_interval:
            self._flush()

    def _flush(self):
        """
        Stub for the intermediate data flush that's triggered during the
        buffering operation.
        """
        raise NotImplementedError()

    def flush(self):
        """
        Stub for the data flush at the end of writing operation.
        """
        raise NotImplementedError()


class FireboltS3Writer(FireboltWriter):
    """
    Data writer using the S3 strategy. Data is buffered in memory
    before being flushed to S3 in .parquet format. At the end of
    the operation data is written to Firebolt databse from S3, allowing
    greater ingestion speed.
    """

    flush_interval = 100000

    def __init__(self, connection: Connection, s3_bucket: str, access_key: str, secret_key: str, s3_region: str) -> None:
        """
        :param connection: Firebolt SDK connection class with established connection
            to the databse.
        :param s3_bucket: Intermediate bucket to store the data files before writing them to Firebolt.
            Has to be created and accessible.
        :param access_key: AWS Access Key ID that has read/write/delete permissions on the files in the bucket.
        :param secret_key: Corresponding AWS Secret Key.
        :param s3_region: S3 region. Best to keep this the same as Firebolt database region. Default us-east-1.
        """
        super().__init__(connection)
        self.key_id = access_key
        self.secret_key = secret_key
        self.s3_bucket = s3_bucket
        self._updated_tables = set()
        self.unique_dir = f"{int(time())}_{uuid4()}"
        self.fs = fs.S3FileSystem(access_key=access_key, secret_key=secret_key, region=s3_region)

    def _flush(self) -> None:
        """
        Intermediate data flush that's triggered during the
        buffering operation. Uploads data stored in memory to the S3.
        """
        for table, data in self._buffer.items():
            key_list, ts_list, payload = zip(*data)
            upload_data = [pa.array(key_list), pa.array(ts_list), pa.array(payload)]
            pa_table = pa.table(upload_data, names=["_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_data"])
            pq.write_to_dataset(table=pa_table, root_path=f"{self.s3_bucket}/airbyte_output/{self.unique_dir}/{table}", filesystem=self.fs)
        # Update tables
        self._updated_tables.update(self._buffer.keys())
        self._buffer.clear()
        self._values = 0

    def flush(self) -> None:
        """
        Flush any leftover data after ingestion and write from S3 to Firebolt.
        Intermediate data on S3 and External Table will be deleted after write is complete.
        """
        self._flush()
        for table in self._updated_tables:
            self.create_raw_table(table)
            self.create_external_table(table)
            self.ingest_data(table)
            self.cleanup(table)

    def create_external_table(self, name: str) -> None:
        """
        Create Firebolt External Table to interface with the files on S3.

        :param name: Stream name from which the table name is derived.
        """
        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS ex_airbyte_raw_{name} (
            _airbyte_ab_id TEXT,
            _airbyte_emitted_at TIMESTAMP,
            _airbyte_data TEXT
        )
        URL = ?
        CREDENTIALS = ( AWS_KEY_ID = ? AWS_SECRET_KEY = ? )
        OBJECT_PATTERN = '*.parquet'
        TYPE = (PARQUET);
        """
        cursor = self.connection.cursor()
        cursor.execute(query, parameters=(f"s3://{self.s3_bucket}/airbyte_output/{self.unique_dir}/{name}", self.key_id, self.secret_key))

    def ingest_data(self, name: str) -> None:
        """
        Write data from External Table to the _airbyte_raw table effectively
        persisting data in Firebolt.

        :param name: Stream name from which the table name is derived.
        """
        query = f"INSERT INTO _airbyte_raw_{name} SELECT * FROM ex_airbyte_raw_{name}"
        cursor = self.connection.cursor()
        cursor.execute(query)

    def cleanup(self, name: str) -> None:
        """
        Clean intermediary External tables and wipe the S3 folder.

        :param name: Stream name from which the table name is derived.
        """
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS ex_airbyte_raw_{name}")
        self.fs.delete_dir_contents(f"{self.s3_bucket}/airbyte_output/{self.unique_dir}/{name}")


class FireboltSQLWriter(FireboltWriter):
    """
    Data writer using the SQL writing strategy. Data is buffered in memory
    and flushed using INSERT INTO SQL statement. This is less effective strategy
    better suited for testing and small data sets.
    """

    flush_interval = 1000

    def __init__(self, connection: Connection) -> None:
        """
        :param connection: Firebolt SDK connection class with established connection
            to the databse.
        """
        super().__init__(connection)

    def _flush(self) -> None:
        """
        Intermediate data flush that's triggered during the
        buffering operation. Writes data stored in memory via SQL commands.
        """
        cursor = self.connection.cursor()
        # id, written_at, data
        for table, data in self._buffer.items():
            cursor.executemany(f"INSERT INTO _airbyte_raw_{table} VALUES (?, ?, ?)", parameters_seq=data)
        self._buffer.clear()
        self._values = 0

    def flush(self) -> None:
        """
        Final data flush after all data has been written to memory.
        """
        self._flush()


def create_firebolt_wirter(connection: Connection, config: json, logger: logging.Logger) -> FireboltWriter:
    if config["loading_method"]["method"] == "S3":
        logger.info("Using the S3 writing strategy")
        writer = FireboltS3Writer(
            connection,
            config["loading_method"]["s3_bucket"],
            config["loading_method"]["aws_key_id"],
            config["loading_method"]["aws_key_secret"],
            config["loading_method"]["s3_region"],
        )
    else:
        logger.info("Using the SQL writing strategy")
        writer = FireboltSQLWriter(connection)
    return writer
