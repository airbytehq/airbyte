#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping, List, Dict, Optional
import random
import json
import os

import pinecone
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Type, Level, ConfiguredAirbyteCatalog, Status, AirbyteRecordMessage, AirbyteLogMessage
from langchain.utils import stringify_dict
from langchain.document_loaders.base import BaseLoader, Document
from langchain.vectorstores.docarray import DocArrayHnswSearch
from langchain.vectorstores import Pinecone
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

BATCH_SIZE = 10


def create_directory_recursively(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        return f"Creation of the directory {path} failed, with error: {str(e)}"
    else:
        return None


class DestinationLangchain(Destination):
    def flush_if_necessary(self):
        if len(self.batch) >= BATCH_SIZE:
            self.flush()

    def flush(self):
        if len(self.batch) == 0:
            return

        docs = []
        for record in self.batch:
            relevant_fields = {k: v for k, v in record.data.items() if k in self.text_fields} if self.text_fields else record.data
            text = stringify_dict(relevant_fields)
            metadata = {k: v for k, v in record.data.items() if k not in self.text_fields} if self.text_fields else {}
            current_stream = record.stream
            # find stream from self.catalog
            for stream in self.catalog.streams:
                if stream.stream.name == current_stream:
                    if stream.primary_key:
                        # todo support composite keys
                        metadata["_natural_id"] = record.data[stream.primary_key[0][0]]
                    break
            docs.append(Document(page_content=text, metadata=metadata))
        chunks = self.splitter.split_documents(docs)
        print(len(chunks))
        # todo: Test all of this stuff
        # extract list of ids from chunks metadata _natural_id field
        ids = [(chunk.metadata["_natural_id"] if "_natural_id" in chunk.metadata else str(uuid.uuid4())) for chunk in chunks]
        # add a chunk number to all chunks with the same id
        id_counts = {}
        for i, id in enumerate(ids):
            if id not in id_counts:
                id_counts[id] = 0
            else:
                id_counts[id] += 1
            ids[i] = id + "_" + str(id_counts[id])
        self.vectorstore.add_documents(chunks, ids)
        self.batch = []

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        self.catalog = configured_catalog
        self.batch: List[AirbyteRecordMessage] = []
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=config.get("processing").get("chunk_size", 1000))
        self.text_fields = config.get("processing").get("text_fields")
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.get("embedding").get("openai_key"))
        if not config.get("storing").get("mode") == "DocArrayHnswSearch":
            pinecone.init(api_key=config.get("storing").get("pinecone_key"), environment=config.get("storing").get("pinecone_environment"))
            index = pinecone.Index(config.get("storing").get("index"))
            # check whether the catalog is using full_refresh mode. If yes, clear the index
            if self.catalog.streams[0].sync_mode == "full_refresh":
                index.delete(delete_all=True)
            self.vectorstore = Pinecone(index, self.embeddings.embed_query, "text")
        else:
            self.vectorstore = DocArrayHnswSearch.from_params(self.embeddings, config.get("storing").get("destination_path"), 1536)
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                yield AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO,message="FLUSHING...."))
                self.flush()
                yield message
            if message.type == Type.RECORD:
                yield AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO,message="Received record: " + json.dumps(message.record.data)))
                self.batch.append(message.record)
                self.flush_if_necessary()
            else:
                continue
        yield AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO,message="FLUSHING.... " + str(len(self.batch))))
        self.flush()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.get("embedding").get("openai_key"))
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))
        if not config.get("storing").get("mode") == "DocArrayHnswSearch":
            try:
                pinecone.init(api_key=config.get("storing").get("pinecone_key"), environment=config.get("storing").get("pinecone_environment"))
                pinecone.describe_index(config.get("storing").get("index"))
            except Exception as e:
                return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            folder_creation_error_message = create_directory_recursively(config.get("storing").get("destination_path"))
            if folder_creation_error_message is not None:
                return AirbyteConnectionStatus(status=Status.FAILED, message=folder_creation_error_message)
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
