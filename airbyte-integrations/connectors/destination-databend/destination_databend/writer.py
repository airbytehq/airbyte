#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from datetime import datetime
from itertools import chain

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from destination_databend.client import DatabendClient


class DatabendWriter:
    """
    Base class for shared writer logic.
    """

    flush_interval = 1000

    def __init__(self, client: DatabendClient) -> None:
        """
        :param client: Databend SDK connection class with established connection
            to the databse.
        """
        try:
            # open a cursor and do some work with it
            self.client = client
            self.cursor = client.open()
            self._buffer = defaultdict(list)
            self._values = 0
        except Exception as e:
            # handle the exception
            raise AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        finally:
            # close the cursor
            self.cursor.close()

    def delete_table(self, name: str) -> None:
        """
        Delete the resulting table.
        Primarily used in Overwrite strategy to clean up previous data.

        :param name: table name to delete.
        """
        self.cursor.execute(f"DROP TABLE IF EXISTS _airbyte_raw_{name}")

    def create_raw_table(self, name: str):
        """
        Create the resulting _airbyte_raw table.

        :param name: table name to create.
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS _airbyte_raw_{name} (
            _airbyte_ab_id TEXT,
            _airbyte_emitted_at TIMESTAMP,
            _airbyte_data TEXT
        )
        """
        cursor = self.cursor
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


class DatabendSQLWriter(DatabendWriter):
    """
    Data writer using the SQL writing strategy. Data is buffered in memory
    and flushed using INSERT INTO SQL statement.
    """

    flush_interval = 1000

    def __init__(self, client: DatabendClient) -> None:
        """
        :param client: Databend SDK connection class with established connection
            to the databse.
        """
        super().__init__(client)

    def _flush(self) -> None:
        """
        Intermediate data flush that's triggered during the
        buffering operation. Writes data stored in memory via SQL commands.
        databend connector insert into table using stage
        """
        cursor = self.cursor
        # id, written_at, data
        for table, data in self._buffer.items():
            cursor.execute(
                f"INSERT INTO _airbyte_raw_{table} (_airbyte_ab_id,_airbyte_emitted_at,_airbyte_data) VALUES (%, %, %)",
                list(chain.from_iterable(data)),
            )
        self._buffer.clear()
        self._values = 0

    def flush(self) -> None:
        """
        Final data flush after all data has been written to memory.
        """
        self._flush()


def create_databend_wirter(client: DatabendClient, logger: AirbyteLogger) -> DatabendWriter:
    logger.info("Using the SQL writing strategy")
    writer = DatabendSQLWriter(client)
    return writer
