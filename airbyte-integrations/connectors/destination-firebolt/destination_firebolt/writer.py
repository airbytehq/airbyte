
from collections import defaultdict

import pyarrow as pa
import pyarrow.parquet as pq
from firebolt.db import Connection
from pyarrow import fs


class FireboltWriter:

    flush_interval = 1000

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self._buffer = defaultdict(list)
        self._values = 0

    def delete_table(self, name: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS _airbyte_raw_{name}")

    def create_raw_table(self, name: str):
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

    def queue_write_data(self, table_name: str, id: str, time: int, record: str) -> None:
        self._buffer[table_name].append((id, time, record))
        self._values += 1
        if self._values == self.flush_interval:
            self._flush()

    def flush(self):
        raise NotImplementedError()

    def _flush(self):
        raise NotImplementedError()


class FireboltS3Writer(FireboltWriter):

    flush_interval = 100000

    def __init__(self, connection: Connection, s3_bucket: str, access_key: str, secret_key: str, s3_region: str) -> None:
        super().__init__(connection)
        self.key_id = access_key
        self.secret_key = secret_key
        self.s3_bucket = s3_bucket
        self._updated_tables = set()
        self.fs = fs.S3FileSystem(access_key=access_key, secret_key=secret_key, region=s3_region)

    def delete_table(self, name: str) -> None:
        super().delete_table(name)
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS ext_airbyte_raw_{name}")

    def create_raw_table(self, name: str):
        super().create_raw_table(name)

    def _flush(self):
        for table, data in self._buffer.items():
            key_list, ts_list, payload = zip(*data)
            upload_data = [pa.array(key_list), pa.array(ts_list), pa.array(payload)]
            pa_table = pa.table(upload_data, names=["_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_data"])
            pq.write_to_dataset(table=pa_table, root_path=f"{self.s3_bucket}/airbyte_output/{table}", filesystem=self.fs)
        # Update tables
        self._updated_tables.update(self._buffer.keys())
        self._buffer.clear()
        self._values = 0

    def flush(self):
        self._flush()
        for table in self._updated_tables:
            self.create_raw_table(table)
            self.create_external_table(table)
            self.ingest_data(table)

    def create_external_table(self, name: str):
        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS ex_airbyte_raw_{name} (
            _airbyte_ab_id TEXT,
            _airbyte_emitted_at TIMESTAMP,
            _airbyte_data TEXT
        )
        URL = 's3://{self.s3_bucket}/airbyte_output/{name}'
        CREDENTIALS = ( AWS_KEY_ID = '{self.key_id}' AWS_SECRET_KEY = '{self.secret_key}' )
        OBJECT_PATTERN = '*.parquet'
        TYPE = (PARQUET);
        """
        cursor = self.connection.cursor()
        cursor.execute(query)

    def ingest_data(self, name: str):
        query = f"INSERT INTO _airbyte_raw_{name} SELECT * FROM ex_airbyte_raw_{name}"
        cursor = self.connection.cursor()
        cursor.execute(query)


class FireboltSQLWriter(FireboltWriter):
    def __init__(self, connection: Connection) -> None:
        super().__init__(connection)

    def _flush(self) -> None:
        cursor = self.connection.cursor()
        # id, written_at, data
        for table, data in self._buffer.items():
            cursor.executemany(f"INSERT INTO _airbyte_raw_{table} VALUES (?, ?, ?)", parameters_seq=data)
        self._buffer.clear()
        self._values = 0

    def flush(self):
        self._flush()
