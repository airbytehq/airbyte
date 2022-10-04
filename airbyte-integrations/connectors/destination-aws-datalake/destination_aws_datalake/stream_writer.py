#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import pandas as pd

from typing import Dict, Any, Optional, List
from destination_aws_datalake.config_reader import ConnectorConfig, PartitionOptions
from airbyte_cdk.models import DestinationSyncMode, ConfiguredAirbyteStream

from .aws import AwsHandler

logger = logging.getLogger("airbyte")


class StreamWriter:
    def __init__(self, aws_handler: AwsHandler, config: ConnectorConfig, configured_stream: ConfiguredAirbyteStream):
        self._aws_handler: AwsHandler = aws_handler
        self._config: ConnectorConfig = config
        self._configured_stream: ConfiguredAirbyteStream = configured_stream
        self._schema: Dict[str, Any] = configured_stream.stream.json_schema["properties"]
        self._sync_mode: DestinationSyncMode = configured_stream.destination_sync_mode

        self._table_exists: bool = False
        self._table: str = configured_stream.stream.name
        self._database: str = self._configured_stream.stream.namespace or self._config.lakeformation_database_name

        self._messages = []
        self._partition_fields = []

        logger.info(f"Creating StreamWriter for {self._database}:{self._table}")

    def _get_path(self) -> str:
        bucket = f"s3://{self._config.bucket_name}"
        if self._config.bucket_prefix:
            bucket += f"/{self._config.bucket_prefix}"

        return f"{bucket}/{self._database}/{self._table}/"

    def _get_date_columns(self) -> list:
        date_columns = []
        for key, val in self._schema.items():
            typ = val.get("type")
            if (isinstance(typ, str) and typ == "string") or (isinstance(typ, list) and "string" in typ):
                if val.get("format") in ["date-time", "date"]:
                    date_columns.append(key)

        return date_columns

    def _add_partition_column(self, col: str, df: pd.DataFrame) -> list:
        partitioning = self._config.partitioning

        if partitioning == PartitionOptions.NONE:
            return []

        partitions = partitioning.value.split("/")

        fields = []
        for partition in partitions:
            date_col = f"{col}_{partition.lower()}"
            if partition == "YEAR":
                df[date_col] = df[col].dt.year

            elif partition == "MONTH":
                df[date_col] = df[col].dt.month

            elif partition == "DAY":
                df[date_col] = df[col].dt.day

            elif partition == "DATE":
                df[date_col] = df[col].dt.date

            fields.append(date_col)

        return fields

    @property
    def _cursor_fields(self) -> Optional[List[str]]:
        return self._configured_stream.cursor_field

    def append_message(self, message):
        self._messages.append(message)

    def reset(self):
        logger.info(f"Deleting table {self._database}:{self._table}")
        success = self._aws_handler.delete_table(self._database, self._table)

        if not success:
            raise Exception(f"Failed to reset table {self._database}:{self._table}")

    def flush(self, force_append=False):
        logger.debug(f"Flushing {len(self._messages)} messages to table {self._database}:{self._table}")

        df = pd.DataFrame(self._messages)

        if len(df) < 1:
            logger.info(f"No messages to write to {self._database}:{self._table}")
            return

        date_columns = self._get_date_columns()
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

                # Create date column for partitioning
                if self._cursor_fields and col in self._cursor_fields:
                    fields = self._add_partition_column(col, df)
                    self._partition_fields.extend(fields)

        if self._sync_mode == DestinationSyncMode.overwrite and not force_append:
            logger.debug(f"Overwriting {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.write(
                df,
                self._get_path(),
                self._database,
                self._table,
                self._partition_fields,
            )

        elif self._sync_mode == DestinationSyncMode.append or force_append:
            logger.debug(f"Appending {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.append(
                df,
                self._get_path(),
                self._database,
                self._table,
                self._partition_fields,
            )

        else:
            self._messages = []
            raise Exception(f"Unsupported sync mode: {self._sync_mode}")

        del df
        self._messages.clear()
