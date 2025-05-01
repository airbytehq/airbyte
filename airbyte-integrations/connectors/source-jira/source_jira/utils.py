#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams import Stream


def safe_max(arg1, arg2):
    if arg1 is None:
        return arg2
    if arg2 is None:
        return arg1
    return max(arg1, arg2)


def read_full_refresh(stream_instance: Stream):
    yield from stream_instance.read_only_records()
