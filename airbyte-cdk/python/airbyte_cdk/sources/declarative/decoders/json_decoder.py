#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


@dataclass
class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        try:
            body_json = response.json()
            if isinstance(body_json, dict):
                body_json = [body_json]
            yield from body_json
        except requests.exceptions.JSONDecodeError:
            yield {}


@dataclass
class IterableDecoder(Decoder):
    """
    Decoder strategy that returns the string content of the response, if any.
    """

    is_stream_response = True
    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        # TODO: how to handle simple string in extractor;
        #  see list_users in iterable:: response.body == b'user1@example.com\nuser2@example.com'
        #  possible option: we can wrap strings directly into records => {"record": {line.decode()}}
        for line in response.iter_lines():
            yield line.decode()


@dataclass
class JsonlDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of the response, if any.
    """

    is_stream_response = True
    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        # TODO???: set delimiter? usually it is `\n` but maybe it would be useful to set optional?
        for record in response.iter_lines():
            yield json.loads(record)
