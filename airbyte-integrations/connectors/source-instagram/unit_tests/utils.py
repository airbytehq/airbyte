#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


def read_full_refresh(stream_instance: AbstractStream):
    records = []
    for partition in stream_instance.generate_partitions():
        records.extend(partition.read())
    return records
