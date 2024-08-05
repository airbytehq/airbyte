# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import datetime
from collections import namedtuple
from pathlib import Path
from typing import TYPE_CHECKING
from concurrent import futures

from airbyte_protocol.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_protocol.models import Type as AirbyteMessageType
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from snoop.schemas import airbyte_message_schema, http_flows_schema
from genson import SchemaBuilder  # type: ignore
import json
from pydantic import ValidationError


from snoop.utils import hash_dict_values, hash_value, sort_dict_keys
from snoop.publish import publish_to_topic
from snoop import logger

if TYPE_CHECKING:
    from pathlib import Path
    from snoop.session import Session
    from typing import List

PUB_SUB_PROJECT_ID = "ab-connector-integration-test"


class ConnectorConfigCollector:
    def get_option_value_path(self, option: str) -> Path:
        for i, arg in enumerate(self.entrypoint_args):
            if arg == option and Path(self.entrypoint_args[i + 1]).exists():
                return Path(self.entrypoint_args[i + 1])
            
    def __init__(self, entrypoint_args: List[str]):
        self.entrypoint_args = entrypoint_args
    
    @property
    def catalog_path(self) -> Path:
        return self.get_option_value_path("--catalog")

    @property
    def config_path(self) -> Path:
        return self.get_option_value_path("--config")
    
    @property
    def state_path(self) -> Path:
        return self.get_option_value_path("--state")
    
    @property
    def catalog(self) -> dict | None:
        if self.catalog_path and self.catalog_path.exists():
            return json.loads(self.catalog_path.read_text())
        
    @property
    def state(self) -> dict | None:
        if self.state_path and self.state_path.exists():
            return json.loads(self.state_path.read_text())
        
    @property
    def config(self) -> dict | None:
        if self.config_path and self.config_path.exists():
            return hash_dict_values(json.loads(self.config_path.read_text()))
        


class ConnectorHttpFlowsCollector:

    CONNECTOR_HTTP_FLOWS_TOPIC = "snoop_http_flows"
    def __init__(self, snoop_session) -> None:
        self.snoop_session = snoop_session
        self.publish_futures = []

    
    def collect(self):
        for flow in self.snoop_session.proxy.get_http_flows_from_mitm_dump():
            record = {
                "snoop_session_id": self.snoop_session.session_id,
                "airbyte_command": self.snoop_session.airbyte_command,
                "connector": self.snoop_session.connector_metadata["data"]["dockerRepository"],
                "connector_version": self.snoop_session.connector_metadata["data"]["dockerImageTag"],
                "request_url": flow.request.url,
                "request_method": flow.request.method,
                "response_status_code": flow.response.status_code,
                "response_time": int((flow.response.timestamp_end - flow.request.timestamp_end) * 1000),
                "response_size": len(flow.response.content),
            }
            logger.info(record)
            self.publish_futures.append(publish_to_topic(PUB_SUB_PROJECT_ID, self.CONNECTOR_HTTP_FLOWS_TOPIC, record, http_flows_schema))

    def wait_for_all_publishes(self) -> None:
        logger.info(f"Waiting for {len(self.publish_futures)} http flow publish to complete")
        futures.wait(self.publish_futures, return_when=futures.ALL_COMPLETED)

class ConnectorMessageCollector:

    SENSITIVE_MESSAGE_TYPES = {AirbyteMessageType.RECORD, AirbyteMessageType.CONTROL}

    # TOPICS
    CONNECTOR_MESSAGES_TOPIC = "snoop_airbyte_message"
    PRIMARY_KEYS_PER_STREAM_TOPIC = "snoop_primary_keys_per_stream"
    OBSERVED_STREAM_SCHEMAS_TOPIC = "snoop_observed_stream_schemas"
    
    def __init__(self, catalog_path: Path | None) -> None:
        self._snoop_session = None
        self.configured_catalog = ConfiguredAirbyteCatalog.parse_file(catalog_path) if catalog_path else None
        self.stream_builders: dict[str, SchemaBuilder] = {}
        self.primary_keys_per_stream: dict[str, list[str]] = {}
        self.publish_futures = []

    def collect(self, line, seen_at: int) -> None:
        try:
            message = AirbyteMessage.parse_raw(line)
            self.publish_message(message, seen_at)
            if message.type is AirbyteMessageType.RECORD:
                self._process_record(message)
        except ValidationError:
            pass
    
    @property
    def snoop_session(self) -> Session:
        if not self._snoop_session:
            raise ValueError("Snoop session not set")
        return self._snoop_session
    
    @snoop_session.setter
    def snoop_session(self, snoop_session: Session) -> None:
        self._snoop_session = snoop_session

    def _process_record(self, airbyte_message):
        self._update_schema(airbyte_message)
        if self.configured_catalog:
            for configured_stream in self.configured_catalog.streams:
                if configured_stream.stream.name == airbyte_message.record.stream:
                    if configured_stream.primary_key:
                        self.primary_keys_per_stream.setdefault(configured_stream.stream.name, [])
                        # TODO handle composite
                        if isinstance(configured_stream.primary_key[0], list):
                            pk = configured_stream.primary_key[0][0]
                        else:
                            pk = configured_stream.primary_key[0]
                        hashed_pk_value = hash_value(airbyte_message.record.data[pk])
                        self.primary_keys_per_stream[configured_stream.stream.name].append(hashed_pk_value)


    def _update_schema(self, record) -> None:
        stream = record.record.stream
        if stream not in self.stream_builders:
            stream_schema_builder = SchemaBuilder()
            stream_schema_builder.add_schema({"type": "object", "properties": {}})
            self.stream_builders[stream] = stream_schema_builder
        self.stream_builders[stream].add_object(record.record.data)

    def _get_stream_schemas(self) -> dict | None:
        return {stream: json.dumps(sort_dict_keys(self.stream_builders[stream].to_schema())) for stream in self.stream_builders}


    def publish_message(self, airbyte_message: AirbyteMessage, seen_at: int) -> None:
        record = {
            "snoop_session_id": self.snoop_session.session_id,
            "airbyte_command": self.snoop_session.airbyte_command,
            "connector": self.snoop_session.connector_metadata["data"]["dockerRepository"],
            "connector_version": self.snoop_session.connector_metadata["data"]["dockerImageTag"],
            "message_type": airbyte_message.type.value,
            "message_size": len(airbyte_message.json().encode("utf-8")),
            "message_timestamp": seen_at,
            "message_content": airbyte_message.json() if airbyte_message.type not in self.SENSITIVE_MESSAGE_TYPES else None
        }
        future = publish_to_topic(PUB_SUB_PROJECT_ID, self.CONNECTOR_MESSAGES_TOPIC, record, airbyte_message_schema)
        self.publish_futures.append(future)

    def publish_primary_keys_per_stream(self) -> None:
        for stream, primary_keys in self.primary_keys_per_stream.items():
            record = {
                "snoop_session_id": self.snoop_session.session_id,
                "airbyte_command": self.snoop_session.airbyte_command,
                "connector": self.snoop_session.connector_metadata["data"]["dockerRepository"],
                "connector_version": self.snoop_session.connector_metadata["data"]["dockerImageTag"],
                "stream": stream,
                "hashed_primary_keys": primary_keys
            }
            publish_to_topic(PUB_SUB_PROJECT_ID, self.PRIMARY_KEYS_PER_STREAM_TOPIC, record)

    def publish_observed_stream_schemas(self) -> None:
        stream_schemas = self._get_stream_schemas()
        for stream, schema in stream_schemas.items():
            record = {
                "snoop_session_id": self.snoop_session.session_id,
                "airbyte_command": self.snoop_session.airbyte_command,
                "connector": self.snoop_session.connector_metadata["data"]["dockerRepository"],
                "connector_version": self.snoop_session.connector_metadata["data"]["dockerImageTag"],
                "stream": stream,
                "schema": schema
            }
            publish_to_topic(PUB_SUB_PROJECT_ID, self.OBSERVED_STREAM_SCHEMAS_TOPIC, record)

    def wait_for_all_publishes(self) -> None:
        logger.info(f"Waiting for {len(self.publish_futures)} message publish to complete")
        futures.wait(self.publish_futures, return_when=futures.ALL_COMPLETED)

# def create_artifact(
#         session_id: str,
#         start_time: int,
#         end_time: int,
#         connector_technical_name: str,
#         airbyte_command: str,
#         config_collector: ConnectorConfigCollector,
#         message_collector: ConnectorMessageCollector,
#         exit_code: int,) -> dict:
#     return{
#             "snoop_session_id": session_id,
#             "start_timestamp": int(start_time.timestamp() * 1000),
#             "end_timestamp": int(end_time.timestamp() * 1000),
#             "airbyte_command": airbyte_command,
#             "connector_technical_name": connector_technical_name,
#             "entrypoint_args": config_collector.entrypoint_args,
#             "config": json.dumps(config_collector.config),
#             "state": json.dumps(config_collector.state),
#             "catalog": json.dumps(config_collector.catalog),
#             "primary_keys_per_stream": message_collector.primary_keys_per_stream,
#             "non_record_messages": [message.json() for message in message_collector.non_record_messages],
#             "stream_schemas": message_collector.get_stream_schemas(),
#             "exit_code": exit_code,
#             "messages_timeline": message_collector.messages_timeline
#         }
    
   