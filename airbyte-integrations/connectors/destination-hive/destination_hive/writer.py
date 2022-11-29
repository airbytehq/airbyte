from airbyte_cdk import AirbyteLogger
import boto3
from boto3.s3.transfer import TransferConfig
from collections import defaultdict
from datetime import datetime
import impala.dbapi
import impala.hiveserver2 as hs2
import json
from logging import getLogger
from time import time
from typing import Any, Dict, Iterable, Mapping, Optional
from uuid import uuid4

class HiveWriter:
    """
    Base class for shared writer logic.
    """

    flush_interval = 1000

    def __init__(self, connection: hs2.HiveServer2Connection, config: Mapping[str, Any], logger: AirbyteLogger) -> None:
        """
        :param connection: Impyla hive connection class with established connection
            to the databse.
        """
        self.connection = connection
        self._buffer = defaultdict(list)
        self._values = 0
        self.logger = logger

    def create_raw_table(self, name: str):
        """
        Create the resulting airbyte_raw table.

        :param name: table name to create.
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS `airbyte_raw_{name}` (
            `airbyte_ab_id` STRING,
            `airbyte_emitted_at` STRING,
            `airbyte_data` STRING,
            PRIMARY KEY (`airbyte_ab_id`) disable novalidate
        )
        """
        self.logger.info(query)
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.close()

    def delete_table(self, name: str) -> None:
        """
        Delete the resulting table.
        Primarily used in Overwrite strategy to clean up previous data.

        :param name: table name to delete.
        """
        cursor = self.connection.cursor()
        query = f"DROP TABLE IF EXISTS `airbyte_raw_{name}`"
        self.logger.info(query)
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


class HiveS3Writer(HiveWriter):
    """
    Data writer using the S3 strategy. Data is buffered in memory
    before being flushed to S3 in .parquet format. At the end of
    the operation data is written to Hive databse from S3, allowing
    greater ingestion speed.
    """

    flush_interval = 100000

    def __init__(self, connection: hs2.HiveServer2Connection, config: Mapping[str, Any], logger: AirbyteLogger) -> None:
        """
        :param connection: Impyla hive connection class with established connection
            to the databse.
        :param s3_bucket: Intermediate bucket to store the data files before writing them to Hive.
            Has to be created and accessible.
        :param access_key: AWS Access Key ID that has read/write/delete permissions on the files in the bucket.
        :param secret_key: Corresponding AWS Secret Key.
        :param s3_region: S3 region. Best to keep this the same as Hive database region. Default us-east-1.
        """
        super().__init__(connection, config, logger)
        self.s3_bucket = config["s3_bucket"]
        self.key_id = config["aws_key_id"]
        self.secret_key = config["aws_key_secret"]
        self.s3_region = config["s3_region"]

        self._updated_tables = set()
        self.s3_unique_dir = f"airbyte_output/{int(time())}_{uuid4()}"
        self.s3_unique_path = f"{self.s3_bucket}/{self.s3_unique_dir}"

        self.boto_session = boto3.Session(
            aws_access_key_id = self.key_id,
            aws_secret_access_key = self.secret_key
            )
        self.boto_client = self.boto_session.client('s3')

    def __del__(self):
        try:
            self.connection.cursor().close()
        except Exception as e:
            self.logger.error("Error closing connection", e)

    def create_external_table(self, name: str):
        """
        Create the resulting airbyte_raw table.

        :param name: table name to create.
        """
        cursor = self.connection.cursor()

        query = f"DROP TABLE IF EXISTS ex_airbyte_raw_{name}"
        self.logger.info(query)
        cursor.execute(query)

        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS ex_airbyte_raw_{name} (
            `airbyte_ab_id` STRING,
            `airbyte_emitted_at` STRING,
            `airbyte_data` STRING
        )
        ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.JsonSerDe'
        STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
        OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
        LOCATION 's3a://{self.s3_unique_path}/{name}/'
        TBLPROPERTIES ( 'classification'='json')
        """
        self.logger.info(query)
        cursor.execute(query)


    def ingest_data(self, name: str) -> None:
        """
        Write data from External Table to the airbyte_raw table effectively
        persisting data in Hive.

        :param name: Stream name from which the table name is derived.
        """
        query = f"""
            INSERT INTO TABLE `airbyte_raw_{name}`
            SELECT airbyte_ab_id, airbyte_emitted_at, airbyte_data FROM ex_airbyte_raw_{name}
        """
        self.logger.info(query)
        cursor = self.connection.cursor()
        cursor.execute(query)

    def cleanup(self, name: str) -> None:
        """
        Clean intermediary External tables and wipe the S3 folder.

        :param name: Stream name from which the table name is derived.
        """
        cursor = self.connection.cursor()
        query = f"DROP TABLE IF EXISTS ex_airbyte_raw_{name}"
        self.logger.info(query)
        cursor.execute(query)
        self.logger.info(f"deleting s3 file {self.s3_unique_path}/{name}/file")
        self.boto_client.delete_object(
            Bucket=self.s3_bucket, 
            Key=f"{self.s3_unique_dir}/{name}/file"
        )

    def _flush(self) -> None:
        """
        Intermediate data flush that's triggered during the
        buffering operation. Uploads data stored in memory to S3.
        """
        self.logger.info("flushing")
        for table, data in self._buffer.items():
            self.logger.info(table)
            ss = ''
            for row in data:
                (key, ts, payload) = row
                js = {}
                js["airbyte_ab_id"] = key
                js["airbyte_emitted_at"] = str(ts)
                js["airbyte_data"] = payload
                # TODO: Fix inefficient way of accumulating rows into a string
                ss += json.dumps(js) + "\n"

            response = self.boto_client.put_object(
                Bucket=self.s3_bucket,
                Key=f"{self.s3_unique_dir}/{table}/file",
                Body=ss.encode())
            self.logger.info(f"response = {response}")
        # Update tables
        self._updated_tables.update(self._buffer.keys())
        self._buffer.clear()
        self._values = 0

    def flush(self) -> None:
        """
        Flush any leftover data after ingestion and write from S3 to Hive.
        Intermediate data on S3 and External Table will be deleted after write is complete.
        """
        self._flush()
        for table in self._updated_tables:
            self.create_raw_table(table)
            self.create_external_table(table)
            self.ingest_data(table)
            self.cleanup(table)

class HiveSQLWriter(HiveWriter):
    """
    Data writer using the SQL writing strategy. Data is buffered in memory
    and flushed using INSERT INTO SQL statement. This is less effective strategy
    better suited for testing and small data sets.
    """

    flush_interval = 1000

    def __init__(self, connection: hs2.HiveServer2Connection, config: Mapping[str, Any], logger: AirbyteLogger) -> None:
        """
        :param connection: Impyla hive connection class with established connection
            to the databse.
        """
        super().__init__(connection, config, logger)

    def _flush(self) -> None:
        """
        Intermediate data flush that's triggered during the
        buffering operation. Writes data stored in memory via SQL commands.
        """
        cursor = self.connection.cursor()
        # id, written_at, data
        for table, data in self._buffer.items():
            cursor.execute(f"INSERT INTO TABLE airbyte_raw_{table} VALUES (?, ?, ?)", parameters_seq=data)
        self._buffer.clear()
        self._values = 0

    def flush(self) -> None:
        """
        Final data flush after all data has been written to memory.
        """
        self._flush()

def create_hive_writer(connection: hs2.HiveServer2Connection, config: Mapping[str, Any], logger: AirbyteLogger) -> HiveWriter:
    if config["loading_method"]["method"] == "S3":
        logger.info("Using S3 to stage data")
        writer = HiveS3Writer(
            connection,
            config["loading_method"],
            logger
        )
    else:
        logger.info("Using the SQL writing strategy")
        writer = HiveSQLWriter(connection, config, logger)
    return writer
