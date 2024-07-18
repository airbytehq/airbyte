# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from airbyte_protocol.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_protocol.models import Type as AirbyteMessageType
from connectors_canary_testing import ARTIFACTS_BUCKET_NAME, logger
from connectors_canary_testing.file_backend import FileBackend
from connectors_canary_testing.utils import hash_dict_values, hash_value, sanitize_stream_name, sort_dict_keys
from genson import SchemaBuilder  # type: ignore
from pydantic import ValidationError

if TYPE_CHECKING:
    from pathlib import Path
    from typing import List


class ArtifactGenerator:
    def __init__(self, artifact_directory: Path, entrypoint_args: List[str]) -> None:
        self.artifact_directory = artifact_directory
        self.artifact_directory.mkdir(exist_ok=True, parents=True)
        self.har_dump_path = self.artifact_directory / "http_traffic.har"
        self.entrypoint_args = entrypoint_args
        self.stream_builders: dict[str, SchemaBuilder] = {}
        self.message_type_counts = {}
        self.messages_to_persist = []
        self._http_flows = None
        self.catalog_path = self.get_option_value_path("--catalog")
        self.config_path = self.get_option_value_path("--config")
        self.state_path = self.get_option_value_path("--state")
        self.catalog = self.get_configured_catalog()
        self.pks_per_stream = {}
        self.bundled_artifacts = {}

    @property
    def http_flows(self):
        return self._http_flows

    @http_flows.setter
    def http_flows(self, http_flows):
        self._http_flows = http_flows

    def process_line(self, line) -> None:
        try:
            message = AirbyteMessage.parse_raw(line)
            self.message_type_counts.setdefault(message.type.value, 0)
            self.message_type_counts[message.type.value] += 1

            if message.type is AirbyteMessageType.RECORD:
                self._process_record(message)
            else:
                self.messages_to_persist.append(message)

        except ValidationError as e:
            pass

    def get_option_value_path(self, option: str) -> Path:
        for i, arg in enumerate(self.entrypoint_args):
            if arg == option and Path(self.entrypoint_args[i + 1]).exists():
                return Path(self.entrypoint_args[i + 1])

    def get_configured_catalog(self) -> ConfiguredAirbyteCatalog | None:
        if self.catalog_path and self.catalog_path.exists():
            return ConfiguredAirbyteCatalog.parse_file(self.catalog_path)

    def _process_record(self, airbyte_message):
        self._update_schema(airbyte_message)
        if self.catalog:
            for configured_stream in self.catalog.streams:
                if configured_stream.stream.name == airbyte_message.record.stream:
                    if configured_stream.primary_key:
                        self.pks_per_stream.setdefault(configured_stream.stream.name, [])
                        # TODO handle composite
                        if isinstance(configured_stream.primary_key[0], list):
                            pk = configured_stream.primary_key[0][0]
                        else:
                            pk = configured_stream.primary_key[0]
                        hashed_pk_value = hash_value(airbyte_message.record.data[pk])
                        self.pks_per_stream[configured_stream.stream.name].append(hashed_pk_value)

        # TODO pks mgmt

    def _update_schema(self, record) -> None:
        stream = record.record.stream
        if stream not in self.stream_builders:
            stream_schema_builder = SchemaBuilder()
            stream_schema_builder.add_schema({"type": "object", "properties": {}})
            self.stream_builders[stream] = stream_schema_builder
        self.stream_builders[stream].add_object(record.record.data)

    def _get_stream_schemas(self) -> dict:
        return {stream: sort_dict_keys(self.stream_builders[stream].to_schema()) for stream in self.stream_builders}

    def _save_messages(self):
        file_backend = FileBackend(self.artifact_directory / "messages")
        file_backend.write(self.messages_to_persist)
        self.bundled_artifacts["messages"] = {}
        for m in self.messages_to_persist:
            self.bundled_artifacts["messages"].setdefault(m.type.value, [])
            self.bundled_artifacts["messages"][m.type.value].append(m.json())

    def _save_stream_schemas(self) -> None:
        stream_schemas_dir = self.artifact_directory / "stream_schemas"
        self.bundled_artifacts["stream_schemas"] = {}
        stream_schemas = self._get_stream_schemas()
        stream_schemas_dir.mkdir(exist_ok=True)
        self.bundled_artifacts["stream_schemas"] = {}
        for stream_name, stream_schema in stream_schemas.items():
            (stream_schemas_dir / f"{sanitize_stream_name(stream_name)}.json").write_text(json.dumps(stream_schema, sort_keys=True))
            self.bundled_artifacts["stream_schemas"][stream_name] = stream_schema

    def _save_entrypoint_args(self) -> None:
        (self.artifact_directory / "entrypoint_args.txt").write_text(" ".join(self.entrypoint_args))
        self.bundled_artifacts["entrypoint_args"] = self.entrypoint_args

    def _save_config(self) -> None:
        if self.config_path:
            config = json.loads(self.config_path.read_text())
            hashed_config = hash_dict_values(config)
            (self.artifact_directory / "config.json").write_text(json.dumps(hashed_config))
            self.bundled_artifacts["config"] = hashed_config

    def _save_catalog(self) -> None:
        if self.catalog_path:
            (self.artifact_directory / "catalog.json").write_text(self.catalog_path.read_text())
            self.bundled_artifacts["configured_catalog"] = json.loads(self.catalog.json())

    def _save_state(self) -> None:
        if self.state_path:
            state = self.state_path.read_text()
            (self.artifact_directory / "state.json").write_text(state)
            self.bundled_artifacts["state"] = json.loads(self.state_path.read_text())

    def _save_message_type_count(self) -> None:
        (self.artifact_directory / "message_type_counts.json").write_text(json.dumps(self.message_type_counts))
        self.bundled_artifacts["message_type_count"] = self.message_type_counts

    def _save_exit_code(self, exit_code) -> None:
        (self.artifact_directory / "exit_code.txt").write_text(str(exit_code))
        self.bundled_artifacts["exit_code"] = exit_code

    def _anonymize_har(self) -> None:
        # TODO strip out secrets from query strings

        if not self.har_dump_path.exists():
            return None
        anonymized_entries = []
        dump = json.loads(self.har_dump_path.read_text())
        for entry in dump["log"]["entries"]:
            entry["request"]["cookies"] = []
            entry["request"]["headers"] = "removed for anonymization"
            entry["response"]["cookies"] = []
            entry["response"]["content"]["text"] = "removed for anonymization"
            anonymized_entries.append(entry)
        dump["log"]["entries"] = anonymized_entries
        self.har_dump_path.write_text(json.dumps(dump))
        self.bundled_artifacts["http_traffic"] = dump

    def _save_pks_per_stream(self) -> None:
        (self.artifact_directory / "pks_per_stream.json").write_text(json.dumps(self.pks_per_stream))
        self.bundled_artifacts["pks_per_streams"] = self.pks_per_stream

    def save_artifacts(self, exit_code):
        self._anonymize_har()
        self._save_exit_code(exit_code)
        self._save_entrypoint_args()
        self._save_messages()
        self._save_catalog()
        self._save_config()
        self._save_state()
        self._save_stream_schemas()
        self._save_message_type_count()
        self._save_pks_per_stream()
        (self.artifact_directory / "bundled_artifacts.json").write_text(json.dumps(self.bundled_artifacts))

    def upload_bundled_artifacts_to_gcs(self, client, bucket_name: str = ARTIFACTS_BUCKET_NAME, destination_blob_prefix: str = ""):

        bucket = client.bucket(bucket_name)
        destination_blob_name = destination_blob_prefix + "_bundled_artifacts.json"

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(str(self.artifact_directory / "bundled_artifacts.json"))

        logger.info(f"Bundled artifacts uploaded to {destination_blob_name}.")
