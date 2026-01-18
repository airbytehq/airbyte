#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream


def run_read(stream_instance: DefaultStream):
    res = []
    schema = stream_instance.get_json_schema()
    partitions = stream_instance._stream_partition_generator.generate()
    for partition in partitions:
        records = partition.read()
        for record in records:
            stream_instance._stream_partition_generator._partition_factory._retriever.record_selector._transform(record, schema)
            res.append(record)
            stream_instance.cursor.observe(record)
        stream_instance.cursor.close_partition(partition)
    return res
