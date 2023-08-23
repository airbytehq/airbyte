#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.models import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from langchain.document_loaders.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utils import stringify_dict

METADATA_STREAM_FIELD = "_airbyte_stream"
METADATA_RECORD_ID_FIELD = "_record_id"


@dataclass
class Chunk:
    page_content: str
    metadata: Dict[str, Any]
    stream: str
    namespace: Optional[str] = None


class DocumentProcessor:
    streams: Mapping[str, ConfiguredAirbyteStream]

    def __init__(self, config: ProcessingConfigModel, catalog: ConfiguredAirbyteCatalog, max_metadata_size: Optional[int] = None):
        self.streams = {self._stream_identifier(stream.stream): stream for stream in catalog.streams}
        self.max_metadata_size = max_metadata_size

        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.text_fields = config.text_fields
        self.metadata_fields = config.metadata_fields
        self.logger = logging.getLogger("airbyte.document_processor")

    def _stream_identifier(self, stream: Union[AirbyteStream, AirbyteRecordMessage]) -> str:
        if isinstance(stream, AirbyteStream):
            return str(stream.name if stream.namespace is None else f"{stream.namespace}_{stream.name}")
        else:
            return str(stream.stream if stream.namespace is None else f"{stream.namespace}_{stream.stream}")

    def process(self, record: AirbyteRecordMessage) -> Tuple[List[Chunk], Optional[str]]:
        """
        Generate documents from records.
        :param records: List of AirbyteRecordMessages
        :return: Tuple of (List of document chunks, record id to delete if a stream is in dedup mode to avoid stale documents in the vector store)
        """
        doc = self._generate_document(record)
        if doc is None:
            self.logger.warning(f"Record {str(record.data)[:250]}... does not contain any text fields. Skipping.")
            return [], None
        chunks = [
            Chunk(
                page_content=chunk_document.page_content, metadata=chunk_document.metadata, stream=record.stream, namespace=record.namespace
            )
            for chunk_document in self._split_document(doc)
        ]
        id_to_delete = doc.metadata[METADATA_RECORD_ID_FIELD] if METADATA_RECORD_ID_FIELD in doc.metadata else None
        return chunks, id_to_delete

    def _generate_document(self, record: AirbyteRecordMessage) -> Optional[Document]:
        relevant_fields = self._extract_relevant_fields(record)
        if len(relevant_fields) == 0:
            return None
        text = stringify_dict(relevant_fields)
        metadata = self._extract_metadata(record)
        return Document(page_content=text, metadata=metadata)

    def _extract_relevant_fields(self, record: AirbyteRecordMessage) -> Dict[str, Any]:
        relevant_fields = {}
        if self.text_fields and len(self.text_fields) > 0:
            for field in self.text_fields:
                values = dpath.util.values(record.data, field, separator=".")
                if values and len(values) > 0:
                    relevant_fields[field] = values
        else:
            relevant_fields = record.data
        return relevant_fields

    def _extract_metadata(self, record: AirbyteRecordMessage) -> Dict[str, Any]:
        metadata = {}
        if self.metadata_fields and len(self.metadata_fields) > 0:
            for field in self.metadata_fields:
                metadata[field] = record.data[field] if field in record.data else None
        else:
            metadata = record.data
        stream_identifier = self._stream_identifier(record)
        current_stream: ConfiguredAirbyteStream = self.streams[stream_identifier]
        metadata[METADATA_STREAM_FIELD] = stream_identifier
        # if the sync mode is deduping, use the primary key to upsert existing records instead of appending new ones
        if current_stream.primary_key and current_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
            metadata[METADATA_RECORD_ID_FIELD] = self._extract_primary_key(record, current_stream)
        return metadata

    def _extract_primary_key(self, record: AirbyteRecordMessage, stream: ConfiguredAirbyteStream) -> str:
        primary_key = []
        for key in stream.primary_key:
            try:
                primary_key.append(str(dpath.util.get(record.data, key)))
            except KeyError:
                primary_key.append("__not_found__")
        return "_".join(primary_key)

    def _split_document(self, doc: Document) -> List[Document]:
        chunks = self.splitter.split_documents([doc])
        return chunks
