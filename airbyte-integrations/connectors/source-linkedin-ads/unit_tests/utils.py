# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream


def run_read(stream_instance: DefaultStream):
    res = []
    partitions = stream_instance.generate_partitions()
    for partition in partitions:
        records = partition.read()
        for record in records:
            res.append(record)
            stream_instance.cursor.observe(record)
        stream_instance.cursor.close_partition(partition)
    return res
