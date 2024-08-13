#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import InitVar, dataclass
from typing import Any, Callable, Generator, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.models.declarative_component_schema import IterableDecoder as IterableDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonDecoder as JsonDecoderModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import JsonDecoder as JsonlDecoderModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.types import Config

logger = logging.getLogger("airbyte")


@dataclass
class JsonDecoder(Decoder, ComponentConstructor[JsonDecoderModel, JsonDecoderModel]):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: JsonDecoderModel,
        config: Config,
        dependency_constructor: Callable[[JsonDecoderModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {"parameters": {}}

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
class IterableDecoder(Decoder, ComponentConstructor[IterableDecoderModel, IterableDecoderModel]):
    """
    Decoder strategy that returns the string content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: IterableDecoderModel,
        config: Config,
        dependency_constructor: Callable[[IterableDecoderModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {"parameters": {}}

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        for line in response.iter_lines():
            yield {"record": line.decode()}


@dataclass
class JsonlDecoder(Decoder, ComponentConstructor[JsonlDecoderModel, JsonlDecoderModel]):
    """
    Decoder strategy that returns the json-encoded content of the response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: JsonlDecoderModel,
        config: Config,
        dependency_constructor: Callable[[JsonlDecoderModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {"parameters": {}}

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        # TODO???: set delimiter? usually it is `\n` but maybe it would be useful to set optional?
        #  https://github.com/airbytehq/airbyte-internal-issues/issues/8436
        for record in response.iter_lines():
            yield json.loads(record)
