#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import nanoid
from airbyte_cdk.models import DestinationSyncMode
from retrying import retry

from .aws import AwsHandler, LakeformationTransaction


class StreamWriter:
    def __init__(self, name, aws_handler: AwsHandler, connector_config, schema, sync_mode):
        self._db = connector_config.lakeformation_database_name
        self._bucket = connector_config.bucket_name
        self._prefix = connector_config.bucket_prefix
        self._table = name
        self._aws_handler = aws_handler
        self._schema = schema
        self._sync_mode = sync_mode
        self._messages = []
        self._logger = aws_handler.logger

        self._logger.debug(f"Creating StreamWriter for {self._db}:{self._table}")
        if sync_mode == DestinationSyncMode.overwrite:
            self._logger.debug(f"StreamWriter mode is OVERWRITE, need to purge {self._db}:{self._table}")
            with LakeformationTransaction(self._aws_handler) as tx:
                self._aws_handler.purge_table(tx.txid, self._db, self._table)

    def append_message(self, message):
        self._logger.debug(f"Appending message to table {self._table}")
        self._messages.append(message)

    def generate_object_key(self, prefix=None):
        salt = nanoid.generate(size=10)
        base = datetime.now().strftime("%Y%m%d%H%M%S")
        path = f"{base}.{salt}.json"
        if prefix:
            path = f"{prefix}/{base}.{salt}.json"

        return path

    @retry(stop_max_attempt_number=10, wait_random_min=2000, wait_random_max=3000)
    def add_to_datalake(self):
        with LakeformationTransaction(self._aws_handler) as tx:
            self._logger.debug(f"Flushing messages to table {self._table}")
            object_prefix = f"{self._prefix}/{self._table}"
            table_location = "s3://" + self._bucket + "/" + self._prefix + "/" + self._table + "/"

            table = self._aws_handler.get_table(tx.txid, self._db, self._table, table_location)
            self._aws_handler.update_table_schema(tx.txid, self._db, table, self._schema)

            if len(self._messages) > 0:
                try:
                    self._logger.debug(f"There are {len(self._messages)} messages to flush for {self._table}")
                    self._logger.debug(f"10 first messages >>> {repr(self._messages[0:10])} <<<")
                    object_key = self.generate_object_key(object_prefix)
                    self._aws_handler.put_object(object_key, self._messages)
                    res = self._aws_handler.head_object(object_key)
                    self._aws_handler.update_governed_table(
                        tx.txid, self._db, self._table, self._bucket, object_key, res["ETag"], res["ContentLength"]
                    )
                    self._logger.debug(f"Table {self._table} was updated")
                except Exception as e:
                    self._logger.error(f"An exception was raised:\n{repr(e)}")
                    raise (e)
            else:
                self._logger.debug(f"There was no message to flush for {self._table}")
        self._messages = []
