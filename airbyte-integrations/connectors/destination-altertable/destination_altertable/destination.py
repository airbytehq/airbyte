import io
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Iterable, Mapping, Union, cast

import orjson
from airbyte_cdk.destinations import Destination
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol_serializers import custom_type_resolver
from serpyco_rs import Serializer
from typing_extensions import override

from .altertable_writer import AltertableWriter

# The patches below are needed for the Python CDK to work with the V2 protocol
# See https://github.com/airbytehq/airbyte/issues/57588
# Inspired by https://github.com/airbytehq/airbyte/blob/f719e8dafe474861f97b949b3bbc606080e3fa11/airbyte-integrations/connectors/destination-motherduck/destination_motherduck/destination.py#L50

logger = getLogger("airbyte")


@dataclass
class PatchedAirbyteStateMessage(AirbyteStateMessage):
    """Declare the `id` attribute that platform sends."""

    id: int | None = None
    """Injected by the platform."""


@dataclass
class PatchedAirbyteMessage(AirbyteMessage):
    """Keep all defaults but override the type used in `state`."""

    state: PatchedAirbyteStateMessage | None = None
    """Override class for the state message only."""


PatchedAirbyteMessageSerializer = Serializer(
    PatchedAirbyteMessage,
    omit_none=True,
    custom_type_resolver=custom_type_resolver,
)
"""Redeclared SerDes class using the patched dataclass."""


class DestinationAltertable(Destination):
    def check(self, logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            with AltertableWriter(config) as writer:
                writer.test_connection()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[Union[AirbyteMessage, AirbyteStateMessage]]:
        with AltertableWriter(config) as writer:
            writer.set_streams(configured_catalog)
            for message in input_messages:
                if message.type == Type.RECORD:
                    writer.buffer_record(message.record)
                elif message.type == Type.STATE:
                    writer.flush()
                    yield message

    @override
    def run(self, args: list[str]) -> None:
        """Overridden from CDK base class in order to use the patched SerDes class."""
        init_uncaught_exception_handler(logger)
        parsed_args = self.parse_args(args)
        output_messages = self.run_cmd(parsed_args)
        for message in output_messages:
            print(
                orjson.dumps(
                    PatchedAirbyteMessageSerializer.dump(
                        cast(PatchedAirbyteMessage, message),
                    )
                ).decode()
            )

    @override
    def _parse_input_stream(
        self, input_stream: io.TextIOWrapper
    ) -> Iterable[AirbyteMessage]:
        """Reads from stdin, converting to Airbyte messages.

        Includes overrides that should be in the CDK but we need to test it in the wild first.

        Rationale:
            The platform injects `id` but our serializer classes don't support
            `additionalProperties`.
        """
        for line in input_stream:
            try:
                yield PatchedAirbyteMessageSerializer.load(orjson.loads(line))
            except orjson.JSONDecodeError:
                logger.info(
                    f"ignoring input which can't be deserialized as Airbyte Message: {line}"
                )
