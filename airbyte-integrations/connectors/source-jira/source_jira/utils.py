#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams import Stream


def read_full_refresh(stream_instance: Stream):
    yield from stream_instance.read_only_records()
