#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import List, Mapping, Optional, Tuple, Union

import dpath.util
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.models.airbyte_protocol import AirbyteStream, DestinationSyncMode
from destination_langchain.config import ProcessingConfigModel
from dpath.exceptions import PathNotFound
from langchain.document_loaders.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utils import stringify_dict

METADATA_STREAM_FIELD = "_airbyte_stream"
METADATA_RECORD_ID_FIELD = "_record_id"


class DocumentProcessor:
    streams: Mapping[str, ConfiguredAirbyteStream]

    def __init__(self, config: ProcessingConfigModel, catalog: ConfiguredAirbyteCatalog, max_metadata_size: Optional[int] = None):
        self.streams = {self._stream_identifier(stream.stream): stream for stream in catalog.streams}
        self.max_metadata_size = max_metadata_size

        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.text_fields = config.text_fields
        self.logger = logging.getLogger("airbyte.document_processor")

    def _stream_identifier(self, stream: Union[AirbyteStream, AirbyteRecordMessage]) -> str:
        if isinstance(stream, AirbyteStream):
            return stream.name if stream.namespace is None else f"{stream.namespace}_{stream.name}"
        else:
            return stream.stream if stream.namespace is None else f"{stream.namespace}_{stream.stream}"

    def process(self, record: AirbyteRecordMessage) -> Tuple[List[Document], Optional[str]]:
        """
        Generate documents from records.
        :param records: List of AirbyteRecordMessages
        :return: Tuple of (List of document chunks, record id to delete if a stream is in dedup mode to avoid stale documents in the vector store)
        """
        doc = self._generate_document(record)
        if doc is None:
            self.logger.warning(f"Record {str(record.data)[:250]}... does not contain any text fields. Skipping.")
            return [], None
        chunks = self._split_document(doc)
        id_to_delete = doc.metadata[METADATA_RECORD_ID_FIELD] if METADATA_RECORD_ID_FIELD in doc.metadata else None
        return chunks, id_to_delete

    def _generate_document(self, record: AirbyteRecordMessage) -> Optional[Document]:
        relevant_fields = self._extract_relevant_fields(record)
        if len(relevant_fields) == 0:
            return None
        metadata = self._extract_metadata(record)
        text = stringify_dict(relevant_fields)
        return Document(page_content=text, metadata=metadata)

    def _extract_relevant_fields(self, record: AirbyteRecordMessage) -> dict:
        relevant_fields = {}
        if self.text_fields:
            for field in self.text_fields:
                values = dpath.util.values(record.data, field, separator=".")
                if values and len(values) > 0:
                    relevant_fields[field] = values
        else:
            relevant_fields = record.data
        return relevant_fields

    def _extract_metadata(self, record: AirbyteRecordMessage) -> dict:
        metadata = record.data
        if self.text_fields:
            for field in self.text_fields:
                try:
                    dpath.util.delete(metadata, field, separator=".")
                except PathNotFound:
                    pass  # if the field doesn't exist, do nothing
        metadata = self._truncate_metadata(metadata)
        stream_identifier = self._stream_identifier(record)
        current_stream = self.streams[stream_identifier]
        metadata[METADATA_STREAM_FIELD] = stream_identifier
        # if the sync mode is deduping, use the primary key to upsert existing records instead of appending new ones
        if current_stream.primary_key and current_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
            # TODO support nested and composite primary keys
            metadata[METADATA_RECORD_ID_FIELD] = record.data[current_stream.primary_key[0][0]]
        return metadata

    def _truncate_metadata(self, metadata: dict) -> dict:
        """
        Normalize metadata to ensure it is within the size limit and doesn't contain complex objects.
        """
        result = {}
        current_size = 0

        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                # Calculate the size of the key and value
                item_size = len(str(key)) + len(str(value))

                # Check if adding the item exceeds the size limit
                if self.max_metadata_size is None or current_size + item_size <= self.max_metadata_size:
                    result[key] = value
                    current_size += item_size

        return result

    def _split_document(self, doc: Document) -> List[Document]:
        chunks = self.splitter.split_documents([doc])
        return chunks
