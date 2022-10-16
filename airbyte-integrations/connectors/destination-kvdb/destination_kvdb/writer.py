#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import Mapping

from destination_kvdb.client import KvDbClient


class KvDbWriter:
    """
    Data is written to KvDB in the following format:
        key: stream_name__ab__<record_extraction_timestamp>
        value: a JSON object representing the record's data

    This is because unless a data source explicitly designates a primary key, we don't know what to key the record on.
    Since KvDB allows reading records with certain prefixes, we treat it more like a message queue, expecting the reader to
    read messages with a particular prefix e.g: name__ab__123, where 123 is the timestamp they last read data from.
    """

    write_buffer = []
    flush_interval = 1000

    def __init__(self, client: KvDbClient):
        self.client = client

    def delete_stream_entries(self, stream_name: str):
        """Deletes all the records belonging to the input stream"""
        keys_to_delete = []
        for key in self.client.list_keys(prefix=f"{stream_name}__ab__"):
            keys_to_delete.append(key)
            if len(keys_to_delete) == self.flush_interval:
                self.client.delete(keys_to_delete)
                keys_to_delete.clear()
        if len(keys_to_delete) > 0:
            self.client.delete(keys_to_delete)

    def queue_write_operation(self, stream_name: str, record: Mapping, written_at: int):
        kv_pair = (f"{stream_name}__ab__{written_at}", record)
        self.write_buffer.append(kv_pair)
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self):
        self.client.batch_write(self.write_buffer)
        self.write_buffer.clear()
