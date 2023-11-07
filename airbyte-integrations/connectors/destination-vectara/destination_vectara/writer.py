#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_vectara.client import VectaraClient



class VectaraWriter:

    write_buffer: List[Mapping[str, Any]] = []
    flush_interval = 1000

    def __init__(self, client: VectaraClient):
        self.client = client

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        streams_to_overwrite = [
            stream.stream.name for stream in catalog.streams if stream.destination_sync_mode == DestinationSyncMode.overwrite
        ]
        if len(streams_to_overwrite):
            self._delete_doc_by_metadata(metadata_field_name=METADATA_STREAM_FIELD, metadata_field_values=streams_to_overwrite)

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            self._delete_doc_by_metadata(metadata_field_name=METADATA_RECORD_ID_FIELD, metadata_field_values=delete_ids)

    def index(self, document_chunks, namespace, stream):
        for chunk in document_chunks:
            self._index_document(chunk=chunk)

    def queue_write_operation(self, message: Mapping[str, Any]) -> None:
        """Adds messages to the write queue and flushes if the buffer is full"""
        self.write_buffer.append(message)
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self) -> None:
        """Writes to Convex"""

        self.client.batch_write(self.write_buffer)
        self.write_buffer.clear()
