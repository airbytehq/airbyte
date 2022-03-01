import json
import nanoid
from datetime import datetime

from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from .aws_helpers import AwsHelper

def generate_key(prefix=None):
    salt = nanoid.generate(size=10)
    base = datetime.now().strftime("%Y%m%d%H%M%S")
    if prefix:
        path = f"{prefix}/{base}.{salt}.txt"
    else:
        path = f"{base}.{salt}.txt"
    return path


class StreamWriter:
    def __init__(self, name, aws_helper: AwsHelper, tx, connector_config, schema, sync_mode):
        self._db = connector_config.DatabaseName
        self._table = name
        self._bucket = connector_config.BucketName
        self._prefix = connector_config.Prefix
        self._aws_helper = aws_helper
        self._tx = tx
        self._schema = schema
        self._sync_mode = sync_mode
        self._messages = []
        self._logger = aws_helper.logger

        self._logger.info(f"Creating StreamWriter for {self._db}:{self._table}")
        if sync_mode == DestinationSyncMode.overwrite:
            self._logger.info(f"StreamWriter mode is OVERWRITE, need to purge {self._db}:{self._table}")
            self._aws_helper.purge_table(self._tx.txid, self._db, self._table)

    def append_message(self, message):
        self._logger.debug(f"Appending message to table {self._table}")
        self._messages.append(message)

    def add_to_datalake(self):
        self._logger.info(f"Flushing messages to table {self._table}")
        object_prefix = f"{self._prefix}/{self._table}"
        object_key = generate_key(object_prefix)
        self._aws_helper.put_object(object_key, self._messages)
        res = self._aws_helper.head_object(object_key)

        table_location = "s3://" + self._bucket + "/" + self._prefix + "/" + self._table + "/"
        table = self._aws_helper.get_table(
            self._tx.txid, self._db, self._table, table_location
        )
        self._aws_helper.update_table_schema(
            self._tx.txid, self._db, table, self._schema
        )

        self._aws_helper.update_governed_table(
            self._tx.txid,
            self._db,
            self._table,
            self._bucket,
            object_key,
            res["ETag"],
            res["ContentLength"]
        )
        self._messages = []
