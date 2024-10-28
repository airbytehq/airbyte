#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from orjson import orjson

logger = logging.getLogger("airbyte")


@dataclass
class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        """
        Given the response is an empty string or an emtpy list, the function will return a generator with an empty mapping.
        """
        try:
            body_json = response.json()
            if not isinstance(body_json, list):
                body_json = [body_json]
            if len(body_json) == 0:
                yield {}
            else:
                yield from body_json
        except requests.exceptions.JSONDecodeError:
            logger.warning(f"Response cannot be parsed into json: {response.status_code=}, {response.text=}")
            yield {}


@dataclass
class IterableDecoder(Decoder):
    """
    Decoder strategy that returns the string content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        for line in response.iter_lines():
            yield {"record": line.decode()}


@dataclass
class JsonlDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        # TODO???: set delimiter? usually it is `\n` but maybe it would be useful to set optional?
        #  https://github.com/airbytehq/airbyte-internal-issues/issues/8436
        for record in response.iter_lines():
            yield orjson.loads(record)
