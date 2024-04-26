#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel, SeparatorSplitterConfigModel, TextSplitterConfigModel
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.utils import stringify_dict
from langchain_core.documents.base import Document

METADATA_STREAM_FIELD = "_ab_stream"
METADATA_RECORD_ID_FIELD = "_ab_record_id"

CDC_DELETED_FIELD = "_ab_cdc_deleted_at"


@dataclass
class Chunk:
    page_content: Optional[str]
    metadata: Dict[str, Any]
    record: AirbyteRecordMessage
    embedding: Optional[List[float]] = None


headers_to_split_on = ["(?:^|\n)# ", "(?:^|\n)## ", "(?:^|\n)### ", "(?:^|\n)#### ", "(?:^|\n)##### ", "(?:^|\n)###### "]


class DocumentProcessor:
    """
    DocumentProcessor is a helper class that generates documents from Airbyte records.

    It is used to generate documents from records before writing them to the destination:
    * The text fields are extracted from the record and concatenated to a single string.
    * The metadata fields are extracted from the record and added to the document metadata.
    * The document is split into chunks of a given size using a langchain text splitter.

    The Writer class uses the DocumentProcessor class to internally generate documents from records - in most cases you don't need to use it directly,
    except if you want to implement a custom writer.

    The config parameters specified by the ProcessingConfigModel has to be made part of the connector spec to allow the user to configure the document processor.
    Calling DocumentProcessor.check_config(config) will validate the config and return an error message if the config is invalid.
    """

    streams: Mapping[str, ConfiguredAirbyteStream]

    @staticmethod
    def check_config(config: ProcessingConfigModel) -> Optional[str]:
        if config.text_splitter is not None and config.text_splitter.mode == "separator":
            for s in config.text_splitter.separators:
                try:
                    separator = json.loads(s)
                    if not isinstance(separator, str):
                        return f"Invalid separator: {s}. Separator needs to be a valid JSON string using double quotes."
                except json.decoder.JSONDecodeError:
                    return f"Invalid separator: {s}. Separator needs to be a valid JSON string using double quotes."
        return None

    def _get_text_splitter(
        self, chunk_size: int, chunk_overlap: int, splitter_config: Optional[TextSplitterConfigModel]
    ) -> RecursiveCharacterTextSplitter:
        if splitter_config is None:
            splitter_config = SeparatorSplitterConfigModel(mode="separator")
        if splitter_config.mode == "separator":
            return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=[json.loads(s) for s in splitter_config.separators],
                keep_separator=splitter_config.keep_separator,
                disallowed_special=(),
            )
        if splitter_config.mode == "markdown":
            return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=headers_to_split_on[: splitter_config.split_level],
                is_separator_regex=True,
                keep_separator=True,
                disallowed_special=(),
            )
        if splitter_config.mode == "code":
            return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=RecursiveCharacterTextSplitter.get_separators_for_language(Language(splitter_config.language)),
                disallowed_special=(),
            )

    def __init__(self, config: ProcessingConfigModel, catalog: ConfiguredAirbyteCatalog):
        self.streams = {create_stream_identifier(stream.stream): stream for stream in catalog.streams}

        self.splitter = self._get_text_splitter(config.chunk_size, config.chunk_overlap, config.text_splitter)
        self.text_fields = config.text_fields
        self.metadata_fields = config.metadata_fields
        self.field_name_mappings = config.field_name_mappings
        self.logger = logging.getLogger("airbyte.document_processor")

    def process(self, record: AirbyteRecordMessage) -> Tuple[List[Chunk], Optional[str]]:
        """
        Generate documents from records.
        :param records: List of AirbyteRecordMessages
        :return: Tuple of (List of document chunks, record id to delete if a stream is in dedup mode to avoid stale documents in the vector store)
        """
        if CDC_DELETED_FIELD in record.data and record.data[CDC_DELETED_FIELD]:
            return [], self._extract_primary_key(record)
        doc = self._generate_document(record)
        if doc is None:
            text_fields = ", ".join(self.text_fields) if self.text_fields else "all fields"
            raise AirbyteTracedException(
                internal_message="No text fields found in record",
                message=f"Record {str(record.data)[:250]}... does not contain any of the configured text fields: {text_fields}. Please check your processing configuration, there has to be at least one text field set in each record.",
                failure_type=FailureType.config_error,
            )
        chunks = [
            Chunk(page_content=chunk_document.page_content, metadata=chunk_document.metadata, record=record)
            for chunk_document in self._split_document(doc)
        ]
        id_to_delete = doc.metadata[METADATA_RECORD_ID_FIELD] if METADATA_RECORD_ID_FIELD in doc.metadata else None
        return chunks, id_to_delete

    def _generate_document(self, record: AirbyteRecordMessage) -> Optional[Document]:
        relevant_fields = self._extract_relevant_fields(record, self.text_fields)
        if len(relevant_fields) == 0:
            return None
        text = stringify_dict(relevant_fields)
        metadata = self._extract_metadata(record)
        return Document(page_content=text, metadata=metadata)

    def _extract_relevant_fields(self, record: AirbyteRecordMessage, fields: Optional[List[str]]) -> Dict[str, Any]:
        relevant_fields = {}
        if fields and len(fields) > 0:
            for field in fields:
                values = dpath.util.values(record.data, field, separator=".")
                if values and len(values) > 0:
                    relevant_fields[field] = values if len(values) > 1 else values[0]
        else:
            relevant_fields = record.data
        return self._remap_field_names(relevant_fields)

    def _extract_metadata(self, record: AirbyteRecordMessage) -> Dict[str, Any]:
        metadata = self._extract_relevant_fields(record, self.metadata_fields)
        metadata[METADATA_STREAM_FIELD] = create_stream_identifier(record)
        primary_key = self._extract_primary_key(record)
        if primary_key:
            metadata[METADATA_RECORD_ID_FIELD] = primary_key
        return metadata

    def _extract_primary_key(self, record: AirbyteRecordMessage) -> Optional[str]:
        stream_identifier = create_stream_identifier(record)
        current_stream: ConfiguredAirbyteStream = self.streams[stream_identifier]
        # if the sync mode is deduping, use the primary key to upsert existing records instead of appending new ones
        if not current_stream.primary_key or current_stream.destination_sync_mode != DestinationSyncMode.append_dedup:
            return None

        primary_key = []
        for key in current_stream.primary_key:
            try:
                primary_key.append(str(dpath.util.get(record.data, key)))
            except KeyError:
                primary_key.append("__not_found__")
        stringified_primary_key = "_".join(primary_key)
        return f"{stream_identifier}_{stringified_primary_key}"

    def _split_document(self, doc: Document) -> List[Document]:
        chunks: List[Document] = self.splitter.split_documents([doc])
        return chunks

    def _remap_field_names(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        if not self.field_name_mappings:
            return fields

        new_fields = fields.copy()
        for mapping in self.field_name_mappings:
            if mapping.from_field in new_fields:
                new_fields[mapping.to_field] = new_fields.pop(mapping.from_field)

        return new_fields
