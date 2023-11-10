#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode

from destination_vectara.client import VectaraClient



METADATA_STREAM_FIELD = "_ab_stream"
# METADATA_RECORD_ID_FIELD = "_ab_record_id"

class VectaraWriter:

    write_buffer: List[Mapping[str, Any]] = []
    flush_interval = 1000

    def __init__(self, client: VectaraClient):
        self.client = client

    def delete_streams_to_overwrite(self, catalog: ConfiguredAirbyteCatalog) -> None:
        streams_to_overwrite = [
            stream.stream.name for stream in catalog.streams if stream.destination_sync_mode == DestinationSyncMode.overwrite
        ]
        if len(streams_to_overwrite):
            self.client._delete_doc_by_metadata(metadata_field_name=METADATA_STREAM_FIELD, metadata_field_values=streams_to_overwrite)

    # def delete_document_to_dedupe(self, delete_ids):
    #     if len(delete_ids) > 0:
    #         self._delete_doc_by_metadata(metadata_field_name=METADATA_RECORD_ID_FIELD, metadata_field_values=delete_ids)

    def queue_write_operation(self, stream_name: str, record: Mapping[str, Any]) -> None:
        """Adds messages to the write queue and flushes if the buffer is full"""
        self.write_buffer.append((stream_name, record))
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self) -> None:
        """Writes to Convex"""

        self.client._index_documents(self.write_buffer)
        self.write_buffer.clear()
