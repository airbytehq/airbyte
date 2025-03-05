#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from box_sdk_gen import BoxAPIError, BoxClient, File, Folder, Items

from airbyte_cdk.models import AirbyteMessage, AirbyteStream, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .box_api import (
    box_folder_ai_ask,
    box_folder_ai_extract,
    box_folder_ai_extract_structured,
    box_folder_text_representation,
    get_box_ccg_client,
)
from .schemas import get_generic_json_schema


logger = logging.getLogger("airbyte")

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type
StreamData = Union[Mapping[str, Any], AirbyteMessage]
"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Source
class SourceBoxDataExtract(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        logger.info("Checking Box API connection...")
        try:
            box_client = get_box_ccg_client(config)
            user = box_client.users.get_user_me()
            logger.debug(f"box_subject_type: {config.get('box_subject_type')}, box_subject_id: {config.get('box_subject_id')}")
            logger.info(f"Logged into Box as: {user.name} ({user.id} - {user.login})")
        except BoxAPIError as e:
            logger.error(f"Unable to connect to Box API with the provided credentials - {e}")
            return False, f"Unable to connect to Box API with the provided credentials"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        box_client = get_box_ccg_client(config)
        box_folder_text_representation_stream = StreamTextRepresentationFolder(
            box_client, config["box_folder_id"], is_recursive=config.get("is_recursive", False)
        )

        box_folder_ask_ai_stream = StreamAIAskFolder(
            box_client, config["box_folder_id"], config["ask_ai_prompt"], is_recursive=config.get("is_recursive", False)
        )

        box_folder_extract_ai_stream = StreamAIExtractFolder(
            box_client, config["box_folder_id"], config["extract_ai_prompt"], is_recursive=config.get("is_recursive", False)
        )

        box_folder_extract_structured_ai_stream = StreamAIExtractStructuredFolder(
            client=box_client,
            folder_id=config["box_folder_id"],
            fields_json_str=config["extract_structured_ai_fields"],
            is_recursive=config.get("is_recursive", False),
        )

        return [
            box_folder_text_representation_stream,
            box_folder_ask_ai_stream,
            box_folder_extract_ai_stream,
            box_folder_extract_structured_ai_stream,
        ]


# Streams
class StreamTextRepresentationFolder(Stream):
    """
    Represents a Box Data Text Representation Stream from a Box Folder.
    params:
        client: BoxClient - Box Client object
        folder_id: str - Box Folder ID
        is_recursive: bool - Whether to read the folder recursively
    """

    client: BoxClient = None
    folder_id: str = None
    is_recursive: bool = False

    def __init__(self, client: BoxClient, folder_id: str, is_recursive: bool = False):
        self.client = client
        self.folder_id = folder_id
        self.is_recursive = is_recursive

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return "id"

    def get_json_schema(self):
        return get_generic_json_schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        logger.info(f"Extracting text representation for files in folder {self.folder_id} {'recursively' if self.is_recursive else ''}")
        items = box_folder_text_representation(self.client, self.folder_id, is_recursive=self.is_recursive)
        for item in items:
            airbyte_item: StreamData = item.file.to_dict()
            airbyte_item["text_representation"] = item.text_representation
            logger.info(f"Reading file {item.file.id} - {item.file.name}")
            yield airbyte_item


class StreamAIAskFolder(Stream):
    client: BoxClient = None
    folder_id: str = None
    is_recursive: bool = False
    prompt: str = None

    def __init__(self, client: BoxClient, folder_id: str, prompt: str, is_recursive: bool = False):
        self.client = client
        self.folder_id = folder_id
        self.is_recursive = is_recursive
        self.prompt = prompt

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return "id"

    def get_json_schema(self):
        return get_generic_json_schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        logger.info(f"Asking AI {self.prompt} for all files in folder {self.folder_id} {'recursively' if self.is_recursive else ''}")
        items = box_folder_ai_ask(self.client, self.folder_id, prompt=self.prompt, is_recursive=self.is_recursive)
        for item in items:
            airbyte_item: StreamData = item.file.to_dict()
            airbyte_item["text_representation"] = item.text_representation
            logger.info(f"Reading file {item.file.id} - {item.file.name}")
            yield airbyte_item


class StreamAIExtractFolder(Stream):
    client: BoxClient = None
    folder_id: str = None
    is_recursive: bool = False
    prompt: str = None

    def __init__(self, client: BoxClient, folder_id: str, prompt: str, is_recursive: bool = False):
        self.client = client
        self.folder_id = folder_id
        self.is_recursive = is_recursive
        self.prompt = prompt

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return "id"

    def get_json_schema(self):
        return get_generic_json_schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        logger.info(f"Extracting AI {self.prompt} for all files in folder {self.folder_id} {'recursively' if self.is_recursive else ''}")
        items = box_folder_ai_extract(self.client, self.folder_id, prompt=self.prompt, is_recursive=self.is_recursive)
        for item in items:
            airbyte_item: StreamData = item.file.to_dict()
            airbyte_item["text_representation"] = item.text_representation
            logger.info(f"Reading file {item.file.id} - {item.file.name}")
            yield airbyte_item


class StreamAIExtractStructuredFolder(Stream):
    client: BoxClient = None
    folder_id: str = None
    is_recursive: bool = False
    fields_json_str: str = None

    def __init__(self, client: BoxClient, folder_id: str, fields_json_str: str, is_recursive: bool = False):
        self.client = client
        self.folder_id = folder_id
        self.is_recursive = is_recursive
        self.fields_json_str = fields_json_str

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """
        return "id"

    def get_json_schema(self):
        return get_generic_json_schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        logger.info(
            f"Extracting Struvctured AI {self.fields_json_str} for all files in folder {self.folder_id} {'recursively' if self.is_recursive else ''}"
        )
        items = box_folder_ai_extract_structured(
            self.client, self.folder_id, fields_json_str=self.fields_json_str, is_recursive=self.is_recursive
        )
        for item in items:
            airbyte_item: StreamData = item.file.to_dict()
            airbyte_item["text_representation"] = item.text_representation
            logger.info(f"Reading file {item.file.id} - {item.file.name}")
            yield airbyte_item
