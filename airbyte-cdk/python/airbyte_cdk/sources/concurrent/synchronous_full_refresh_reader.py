#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent.full_refresh_stream_reader import FullRefreshStreamReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logging import create_slice_log_message, should_log_slice_message


class SyncrhonousFullRefreshReader(FullRefreshStreamReader):
    def read_stream(self, stream: Stream, cursor_field, logger, internal_config=InternalConfig()):
        slices = stream.generate_partitions(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field)
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        for _slice in slices:
            if should_log_slice_message(logger):
                yield create_slice_log_message(_slice)
            record_data_or_messages = stream.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
            )
            for record_data_or_message in record_data_or_messages:
                yield record_data_or_message
                if FullRefreshStreamReader.is_record(record_data_or_message):
                    total_records_counter += 1
                    if internal_config and internal_config.limit_reached(total_records_counter):
                        return
