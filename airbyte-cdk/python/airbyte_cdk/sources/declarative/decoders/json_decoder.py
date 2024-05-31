#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


@dataclass
class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List[Any], Any]:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {}


@dataclass
class IterableDecoder(Decoder):
    """
    Decoder strategy that returns the string content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List[Any], Any]:
        # TODO: how to handle simple string in extractor
        for record in response.iter_lines():
            yield record.decode()


@dataclass
class JsonlDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List[Any], Any]:
        # TODO???: set delimiter? usually it is `\n` but maybe it would be useful to set optional
        for record in response.iter_lines():
            yield json.loads(record)
