#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder

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
        try:
            body_json = response.json()
            if not isinstance(body_json, list):
                body_json = [body_json]
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
            yield json.loads(record)
