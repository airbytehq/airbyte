#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from abc import abstractmethod
from typing import Any, Iterator, MutableMapping, Tuple

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteStream
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig


class DeclarativeSource(AbstractSource):
    """
    Base class for declarative Source. Concrete sources need to define the connection_checker to use
    """

    @property
    @abstractmethod
    def connection_checker(self) -> ConnectionChecker:
        pass

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return self.connection_checker.check_connection(self, logger, config)

    def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        generator = super()._read_incremental(logger, stream_instance, configured_stream, connector_state, internal_config)
        at_least_one_record_was_read = False
        for record in generator:
            at_least_one_record_was_read = True
            yield record
        if not at_least_one_record_was_read:
            yield self._checkpoint_state(stream_instance, stream_instance.state, connector_state)
