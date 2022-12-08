#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode


class StreamHelper:
    @staticmethod
    def get_stream_slice(stream):
        # We wrap the return output of stream_slices() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        slices = iter(
            stream.stream_slices(
                cursor_field=stream.cursor_field,
                sync_mode=SyncMode.full_refresh,
            )
        )
        try:
            return next(slices)
        except StopIteration:
            return {}
