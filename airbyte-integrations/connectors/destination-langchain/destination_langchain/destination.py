#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping, List, Dict
import random
import json

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Type, Level, ConfiguredAirbyteCatalog, Status, AirbyteRecordMessage, AirbyteLogMessage
from langchain.utils import stringify_dict
from langchain.document_loaders.base import BaseLoader, Document
from langchain.vectorstores.weaviate import Weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import weaviate
import string


BATCH_SIZE = 10


class DestinationLangchain(Destination):
    def flush_if_necessary(self):
        if len(self.batch) >= BATCH_SIZE:
            self.flush()

    def flush(self):
        if len(self.batch) == 0:
            return

        docs = []
        metadata = {}
        for record in self.batch:
            text = stringify_dict(record.data)
            docs.append(Document(page_content=text, metadata=metadata))
        chunks = self.splitter.split_documents(docs)
        print(len(chunks))
        self.vectorstore.add_documents(chunks)
        self.batch = []

    def get_client(self, config: Mapping[str, Any]):
        return weaviate.Client(
            url=config.get("storing").get("weaviate_url"),
            auth_client_secret=weaviate.AuthApiKey(config.get("storing").get("weaviate_key")),
            additional_headers={"X-OpenAI-Api-Key": config.get("processing").get("openai_key")},
        )

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        self.batch: List[AirbyteRecordMessage] = []
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=config.get("processing").get("chunk_size", 1000))
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.get("processing").get("openai_key"))
        self.vectorstore = Weaviate(
            client=self.get_client(config),
            embedding=self.embeddings,
            index_name=config.get("storing").get("index_name"),
            text_key="content"
        )
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                yield AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO,message="FLUSHING...."))
                # self.flush()
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
        client = self.get_client(config)
        if client.is_ready() == False:
            return AirbyteConnectionStatus(status=Status.FAILED, message="Weaviate is not ready")
        
        class_name = "".join(random.choices(string.ascii_uppercase, k=10))
        client.schema.create_class({"class": class_name})
        client.schema.delete_class(class_name)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
