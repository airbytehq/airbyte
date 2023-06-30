from typing import List, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog
from langchain.document_loaders.base import Document
from langchain.utils import stringify_dict
import dpath.util
from dpath.exceptions import PathNotFound
import uuid


class Processor:
    def __init__(self, config: dict):
        self.config = config
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=config.get("chunk_size", 1000),
            chunk_overlap=config.get("chunk_overlap", 0)
        )
        self.text_fields = config.get("text_fields")

    def process(self, record: AirbyteRecordMessage) -> Tuple[List[Document], List[str], List[str]]:
        """
        Generate documents from records.
        :param records: List of AirbyteRecordMessages
        :return: Tuple of (List of document chunks, List of IDs matching the documents chunks, List of natural ids to delete)
        """
        docs = self.generate_document(record)
        chunks = self.split_documents(docs)
        chunk_ids, ids_to_delete = self.generate_ids(chunks)
        return chunks, chunk_ids, ids_to_delete

    def generate_document(self, record: List[AirbyteRecordMessage]) -> Document:
        relevant_fields = self.extract_relevant_fields(record)
        text = stringify_dict(relevant_fields)
        metadata = self.extract_metadata(record, relevant_fields)
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

    def extract_metadata(self, record: AirbyteRecordMessage, relevant_fields: dict) -> dict:
        metadata = record.data.copy()
        for field in self.text_fields:
            try:
                dpath.util.delete(metadata, field, separator=".")
            except PathNotFound:
                pass  # if the field doesn't exist, do nothing
        metadata = self._normalize_metadata(metadata)
        current_stream = record.stream
        metadata["_airbyte_stream"] = current_stream
        for stream in self.catalog.streams:
            if stream.stream.name == current_stream:
                if stream.primary_key:
                    metadata["_natural_id"] = record.data[stream.primary_key[0][0]]
                break
        return metadata
    
    def _normalize_metadata(self, metadata: dict) -> dict:
        return {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }

    def split_documents(self, docs: List[Document]) -> List[Document]:
        chunks = self.splitter.split_documents(docs)
        return chunks

    def generate_ids(self, chunks: List[Document]) -> Tuple[List[str], List[str]]:
        ids = self.extract_ids(chunks)
        return self.build_chunk_ids(ids)

    def extract_ids(self, chunks: List[Document]) -> List[str]:
        ids = [
            chunk.metadata["_natural_id"] if "_natural_id" in chunk.metadata else str(uuid.uuid4())
            for chunk in chunks
        ]
        return ids

    def build_chunk_ids(self, ids: List[str]) -> Tuple[List[str], List[str]]:
        id_counts = {}
        ids_to_delete = []
        for i, doc_id in enumerate(ids):
            if doc_id not in id_counts:
                id_counts[doc_id] = 0
                ids_to_delete.append(doc_id)
            else:
                id_counts[doc_id] += 1
            ids[i] = f"{doc_id}_{id_counts[doc_id]}"
        return ids, ids_to_delete