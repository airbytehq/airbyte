#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import os
import selectors
import subprocess
from dataclasses import dataclass
from datetime import datetime
from io import TextIOWrapper
from typing import Any, DefaultDict, Dict, Iterator, List, Mapping, Optional, Tuple

from airbyte_cdk.logger import log_by_prefix
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    SyncMode,
    Type,
)

_INCREMENTAL = "INCREMENTAL"
_FULL_TABLE = "FULL_TABLE"


def to_json(string):
    try:
        return json.loads(string)
    except ValueError:
        return False


def is_field_metadata(metadata):
    if len(metadata.get("breadcrumb")) != 2:
        return False
    else:
        return metadata.get("breadcrumb")[0] != "property"


def configured_for_incremental(configured_stream: ConfiguredAirbyteStream):
    return configured_stream.sync_mode and configured_stream.sync_mode == SyncMode.incremental


def get_stream_level_metadata(metadatas: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for metadata in metadatas:
        if not is_field_metadata(metadata) and "metadata" in metadata:
            return metadata.get("metadata")
    return None


@dataclass
class Catalogs:
    singer_catalog: object
    airbyte_catalog: AirbyteCatalog


@dataclass
class SyncModeInfo:
    supported_sync_modes: Optional[List[SyncMode]] = None
    source_defined_cursor: Optional[bool] = None
    default_cursor_field: Optional[List[str]] = None


def set_sync_modes_from_metadata(airbyte_stream: AirbyteStream, metadatas: List[Dict[str, Any]]):
    stream_metadata = get_stream_level_metadata(metadatas)
    if stream_metadata:
        # A stream is incremental if it declares replication keys or if forced-replication-method is set to incremental
        replication_keys = stream_metadata.get("valid-replication-keys", [])
        if len(replication_keys) > 0:
            airbyte_stream.source_defined_cursor = True
            airbyte_stream.supported_sync_modes = [SyncMode.incremental]
            # TODO if there are multiple replication keys, allow configuring which one is used. For now we deterministically take the first
            airbyte_stream.default_cursor_field = [sorted(replication_keys)[0]]
        elif "forced-replication-method" in stream_metadata:
            forced_replication_method = stream_metadata["forced-replication-method"]
            if isinstance(forced_replication_method, dict):
                forced_replication_method = forced_replication_method.get("replication-method", "")
            if forced_replication_method.upper() == _INCREMENTAL:
                airbyte_stream.source_defined_cursor = True
                airbyte_stream.supported_sync_modes = [SyncMode.incremental]
            elif forced_replication_method.upper() == _FULL_TABLE:
                airbyte_stream.source_defined_cursor = False
                airbyte_stream.supported_sync_modes = [SyncMode.full_refresh]


def override_sync_modes(airbyte_stream: AirbyteStream, overrides: SyncModeInfo):
    airbyte_stream.source_defined_cursor = overrides.source_defined_cursor or False
    if overrides.supported_sync_modes:
        airbyte_stream.supported_sync_modes = overrides.supported_sync_modes
    if overrides.default_cursor_field is not None:
        airbyte_stream.default_cursor_field = overrides.default_cursor_field


class SingerHelper:
    @staticmethod
    def _transform_types(stream_properties: DefaultDict):
        for field_name in stream_properties:
            field_object = stream_properties[field_name]
            # according to issue CDK: typing errors #9500, mypy raises error on this line
            # '"Type[SingerHelper]" has no attribute "_parse_type"', it's need to fix
            # ignored for now
            field_object["type"] = SingerHelper._parse_type(field_object["type"])  # type: ignore

    @staticmethod
    def singer_catalog_to_airbyte_catalog(
        singer_catalog: Dict[str, Any], sync_mode_overrides: Dict[str, SyncModeInfo], primary_key_overrides: Dict[str, List[str]]
    ) -> AirbyteCatalog:
        """
        :param singer_catalog:
        :param sync_mode_overrides: A dict from stream name to the sync modes it should use. Each stream in this dict must exist in the Singer catalog,
          but not every stream in the catalog should exist in this
        :param primary_key_overrides: A dict of stream name -> list of fields to be used as PKs.
        :return: Airbyte Catalog
        """
        airbyte_streams = []
        # according to issue CDK: typing errors #9500, mypy raises error on this line
        # 'Item "None" of "Optional[Any]" has no attribute "__iter__" (not iterable)'
        # It occurs because default value isn't set, and it's None
        # It's needed to set default value, ignored for now
        for stream in singer_catalog.get("streams"):  # type: ignore
            name = stream.get("stream")
            schema = stream.get("schema")
            airbyte_stream = AirbyteStream(name=name, json_schema=schema, supported_sync_modes=[SyncMode.full_refresh])
            if name in sync_mode_overrides:
                override_sync_modes(airbyte_stream, sync_mode_overrides[name])
            else:
                set_sync_modes_from_metadata(airbyte_stream, stream.get("metadata", []))

            if name in primary_key_overrides:
                airbyte_stream.source_defined_primary_key = [[k] for k in primary_key_overrides[name]]
            elif stream.get("key_properties"):
                airbyte_stream.source_defined_primary_key = [[k] for k in stream["key_properties"]]

            airbyte_streams += [airbyte_stream]
        return AirbyteCatalog(streams=airbyte_streams)

    @staticmethod
    def _read_singer_catalog(logger, shell_command: str) -> Mapping[str, Any]:
        completed_process = subprocess.run(
            shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        for line in completed_process.stderr.splitlines():
            logger.log(*log_by_prefix(line, "ERROR"))

        return json.loads(completed_process.stdout)

    @staticmethod
    def get_catalogs(
        logger,
        shell_command: str,
        sync_mode_overrides: Dict[str, SyncModeInfo],
        primary_key_overrides: Dict[str, List[str]],
        excluded_streams: List,
    ) -> Catalogs:
        singer_catalog = SingerHelper._read_singer_catalog(logger, shell_command)
        streams = singer_catalog.get("streams", [])
        if streams and excluded_streams:
            # according to issue CDK: typing errors #9500, mypy raises error on this line
            # 'Unsupported target for indexed assignment ("Mapping[str, Any]")'
            # _read_singer_catalog returns Mapping, to fix this error it should be changed to MutableMapping
            # ignored for now
            singer_catalog["streams"] = [stream for stream in streams if stream["stream"] not in excluded_streams]  # type: ignore

        # according to issue CDK: typing errors #9500, mypy raises error on this line
        # 'Argument 1 to "singer_catalog_to_airbyte_catalog" of "SingerHelper" has incompatible type "Mapping[str, Any]"; expected "Dict[str, Any]"'
        # singer_catalog is Mapping, because _read_singer_catalog returns Mapping, but singer_catalog_to_airbyte_catalog expects Dict
        # it's needed to check and fix, ignored for now
        airbyte_catalog = SingerHelper.singer_catalog_to_airbyte_catalog(singer_catalog, sync_mode_overrides, primary_key_overrides)  # type: ignore
        return Catalogs(singer_catalog=singer_catalog, airbyte_catalog=airbyte_catalog)

    @staticmethod
    def read(logger, shell_command, is_message=(lambda x: True)) -> Iterator[AirbyteMessage]:
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as p:
            for line, text_wrapper in SingerHelper._read_lines(p):
                if text_wrapper is p.stdout:
                    out_json = to_json(line)
                    if out_json is not None and is_message(out_json):
                        message_data = SingerHelper._airbyte_message_from_json(out_json)
                        if message_data is not None:
                            yield message_data
                    else:
                        logger.log(*log_by_prefix(line, "INFO"))
                else:
                    logger.log(*log_by_prefix(line, "ERROR"))

    @staticmethod
    def _read_lines(process: subprocess.Popen) -> Iterator[Tuple[str, TextIOWrapper]]:
        sel = selectors.DefaultSelector()
        # according to issue CDK: typing errors #9500, mypy raises error on this two lines
        # 'Argument 1 to "register" of "DefaultSelector" has incompatible type "Optional[IO[Any]]"; expected "Union[int, HasFileno]"'
        # 'Argument 1 to "register" of "DefaultSelector" has incompatible type "Optional[IO[Any]]"; expected "Union[int, HasFileno]"'
        # It's need to check, ignored for now
        sel.register(process.stdout, selectors.EVENT_READ)  # type: ignore
        sel.register(process.stderr, selectors.EVENT_READ)  # type: ignore
        eof = False
        while not eof:
            selects_list = sel.select()
            empty_line_counter = 0
            for key, _ in selects_list:
                # according to issue CDK: typing errors #9500, mypy raises two errors on these lines
                # 'Item "int" of "Union[int, HasFileno]" has no attribute "readline"'
                # 'Item "HasFileno" of "Union[int, HasFileno]" has no attribute "readline"'
                # It's need to check, ignored for now
                line = key.fileobj.readline()  # type: ignore
                if not line:
                    empty_line_counter += 1
                    if empty_line_counter >= len(selects_list):
                        eof = True

                        try:
                            process.wait(timeout=60)
                        except subprocess.TimeoutExpired:
                            # according to issue CDK: typing errors #9500, mypy raises error on this line
                            # 'On Python 3 '{}'.format(b'abc') produces "b'abc'", not 'abc'; use '{!r}'.format(b'abc') if this is desired behavior'
                            # It's need to fix, ignored for now
                            raise Exception(f"Underlying command {process.args} is hanging")  # type: ignore

                        if process.returncode != 0:
                            # according to issue CDK: typing errors #9500, mypy raises error on this line
                            # 'On Python 3 '{}'.format(b'abc') produces "b'abc'", not 'abc'; use '{!r}'.format(b'abc') if this is desired behavior'
                            # It's need to fix, ignored for now
                            raise Exception(f"Underlying command {process.args} failed with exit code {process.returncode}")  # type: ignore
                else:
                    # according to issue CDK: typing errors #9500, mypy raises error on this line
                    # 'Incompatible types in "yield" (actual type "Tuple[Any, Union[int, HasFileno]]", expected type "Tuple[str, TextIOWrapper]")'
                    # It's need to fix, ignored for now
                    yield line, key.fileobj  # type: ignore

    @staticmethod
    def _airbyte_message_from_json(transformed_json: Mapping[str, Any]) -> Optional[AirbyteMessage]:
        if transformed_json is None or transformed_json.get("type") == "SCHEMA" or transformed_json.get("type") == "ACTIVATE_VERSION":
            return None
        elif transformed_json.get("type") == "STATE":
            out_record = AirbyteStateMessage(data=transformed_json["value"])
            out_message = AirbyteMessage(type=Type.STATE, state=out_record)
        else:
            # todo: check that messages match the discovered schema
            stream_name = transformed_json["stream"]
            # according to issue CDK: typing errors #9500, mypy raises error on this line
            # 'Incompatible types in assignment (expression has type "AirbyteRecordMessage", variable has type "AirbyteStateMessage")'
            # type of out_record is first initialized as AirbyteStateMessage on the line 240
            # however AirbyteRecordMessage is assigned on the line below, it causes error
            # ignored
            out_record = AirbyteRecordMessage(  # type: ignore
                stream=stream_name,
                data=transformed_json["record"],
                emitted_at=int(datetime.now().timestamp()) * 1000,
            )
            out_message = AirbyteMessage(type=Type.RECORD, record=out_record)
        return out_message

    @staticmethod
    def create_singer_catalog_with_selection(masked_airbyte_catalog: ConfiguredAirbyteCatalog, discovered_singer_catalog: object) -> str:
        combined_catalog_path = os.path.join("singer_rendered_catalog.json")
        masked_singer_streams = []

        stream_name_to_configured_stream = {
            configured_stream.stream.name: configured_stream for configured_stream in masked_airbyte_catalog.streams
        }

        # according to issue CDK: typing errors #9500, mypy raises error on this line
        # '"object" has no attribute "get"'
        # discovered_singer_catalog type is set to object on the line 259, need to check
        # ignored for now
        for singer_stream in discovered_singer_catalog.get("streams"):  # type: ignore
            stream_name = singer_stream.get("stream")
            if stream_name in stream_name_to_configured_stream:
                new_metadatas = []
                # support old style catalog.
                singer_stream["schema"]["selected"] = True
                if singer_stream.get("metadata"):
                    metadatas = singer_stream.get("metadata")
                    for metadata in metadatas:
                        new_metadata = metadata
                        new_metadata["metadata"]["selected"] = True
                        if not is_field_metadata(new_metadata):
                            configured_stream = stream_name_to_configured_stream[stream_name]
                            if configured_for_incremental(configured_stream):
                                replication_method = _INCREMENTAL
                                if configured_stream.cursor_field:
                                    new_metadata["metadata"]["replication-key"] = configured_stream.cursor_field[0]
                            else:
                                replication_method = _FULL_TABLE
                            new_metadata["metadata"]["forced-replication-method"] = replication_method
                            new_metadata["metadata"]["replication-method"] = replication_method
                        else:
                            if "fieldExclusions" in new_metadata["metadata"]:
                                new_metadata["metadata"]["selected"] = True if not new_metadata["metadata"]["fieldExclusions"] else False
                        new_metadatas += [new_metadata]
                    singer_stream["metadata"] = new_metadatas

            masked_singer_streams += [singer_stream]

        combined_catalog = {"streams": masked_singer_streams}
        with open(combined_catalog_path, "w") as fh:
            fh.write(json.dumps(combined_catalog))

        return combined_catalog_path
