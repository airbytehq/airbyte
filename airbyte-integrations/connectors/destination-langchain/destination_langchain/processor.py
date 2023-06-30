from typing import List, Tuple, Mapping
from destination_langchain.config import ProcessingConfigModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from langchain.document_loaders.base import Document
from langchain.utils import stringify_dict
import dpath.util
from dpath.exceptions import PathNotFound
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
import uuid
from dataclasses import dataclass

METADATA_STREAM_FIELD = "_airbyte_stream"
METADATA_NATURAL_ID_FIELD = "_natural_id"


@dataclass
class DocumentIdentifier:
    id: str
    stream: str


class Processor:
    streams: Mapping[str, ConfiguredAirbyteStream]

    def __init__(self, config: ProcessingConfigModel, catalog: ConfiguredAirbyteCatalog):
        self.streams = {stream.stream.name: stream for stream in catalog.streams}

        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.text_fields = config.text_fields

    def process(self, record: AirbyteRecordMessage) -> Tuple[List[Document], List[str], List[str]]:
        """
        Generate documents from records.
        :param records: List of AirbyteRecordMessages
        :return: Tuple of (List of document chunks, List of IDs matching the documents chunks, List of natural ids to delete)
        """
        doc = self.generate_document(record)
        chunks = self.split_document(doc)
        chunk_ids, ids_to_delete = self.generate_ids(chunks)
        return chunks, chunk_ids, ids_to_delete

    def generate_document(self, record: AirbyteRecordMessage) -> Document:
        relevant_fields = self.extract_relevant_fields(record)
        metadata = self.extract_metadata(record)
        text = stringify_dict(relevant_fields)
        return Document(page_content=text, metadata=metadata)

    def extract_relevant_fields(self, record: AirbyteRecordMessage) -> dict:
        relevant_fields = {}
        if self.text_fields:
            for field in self.text_fields:
                relevant_fields[field] = dpath.util.values(record.data, field, separator=".")
                if len(relevant_fields[field]) == 1:
                    relevant_fields[field] = relevant_fields[field][0]
        else:
            relevant_fields = record.data
        return relevant_fields

    def extract_metadata(self, record: AirbyteRecordMessage) -> dict:
        metadata = record.data.copy()
        for field in self.text_fields:
            try:
                dpath.util.delete(metadata, field, separator=".")
            except PathNotFound:
                pass  # if the field doesn't exist, do nothing
        metadata = self._normalize_metadata(metadata)
        current_stream = self.streams[record.stream]
        metadata[METADATA_STREAM_FIELD] = record.stream
        # if the sync mode is deduping, use the primary key to upsert existing records instead of appending new ones
        if current_stream.primary_key and current_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
            # TODO support nested and composite primary keys
            metadata[METADATA_NATURAL_ID_FIELD] = record.data[current_stream.primary_key[0][0]]
        return metadata

    def _normalize_metadata(self, metadata: dict) -> dict:
        return {key: value for key, value in metadata.items() if isinstance(value, (str, int, float, bool))}

    def split_document(self, doc: Document) -> List[Document]:
        chunks = self.splitter.split_documents([doc])
        return chunks

    def generate_ids(self, chunks: List[Document]) -> Tuple[List[str], List[str]]:
        ids = self.extract_document_ids(chunks)
        return self.build_chunk_ids(ids)

    def extract_document_ids(self, chunks: List[Document]) -> List[DocumentIdentifier]:
        ids = [
            DocumentIdentifier(
                chunk.metadata[METADATA_NATURAL_ID_FIELD] if METADATA_NATURAL_ID_FIELD in chunk.metadata else str(uuid.uuid4()),
                chunk.metadata[METADATA_STREAM_FIELD],
            )
            for chunk in chunks
        ]
        return ids

    def build_chunk_ids(self, identifiers: List[DocumentIdentifier]) -> Tuple[List[str], List[str]]:
        id_counts = {}
        ids_to_delete = []
        ids = [None] * len(identifiers)
        for i, doc_identifier in enumerate(identifiers):
            id = doc_identifier.id
            if id not in id_counts:
                id_counts[id] = 0
                if self.streams[doc_identifier.stream].destination_sync_mode == DestinationSyncMode.append_dedup:
                    ids_to_delete.append(id)
            else:
                id_counts[id] += 1
            ids[i] = f"{id}_{id_counts[id]}"
        return ids, ids_to_delete
