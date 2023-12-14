#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional, TypeVar

from airbyte_cdk.connector import TConfig
from airbyte_cdk.sources.embedded.catalog import create_configured_catalog, get_stream, get_stream_names
from airbyte_cdk.sources.embedded.runner import SourceRunner
from airbyte_cdk.sources.embedded.tools import get_defined_id
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_protocol.models import AirbyteRecordMessage, AirbyteStateMessage, SyncMode, Type

TOutput = TypeVar("TOutput")


class BaseEmbeddedIntegration(ABC, Generic[TConfig, TOutput]):
    def __init__(self, runner: SourceRunner[TConfig], config: TConfig):
        check_config_against_spec_or_exit(config, runner.spec())

        self.source = runner
        self.config = config

        self.last_state: Optional[AirbyteStateMessage] = None

    @abstractmethod
    def _handle_record(self, record: AirbyteRecordMessage, id: Optional[str]) -> Optional[TOutput]:
        """
        Turn an Airbyte record into the appropriate output type for the integration.
        """
        pass

    def _load_data(self, stream_name: str, state: Optional[AirbyteStateMessage] = None) -> Iterable[TOutput]:
        catalog = self.source.discover(self.config)
        stream = get_stream(catalog, stream_name)
        if not stream:
            raise ValueError(f"Stream {stream_name} not found, the following streams are available: {', '.join(get_stream_names(catalog))}")
        if SyncMode.incremental not in stream.supported_sync_modes:
            configured_catalog = create_configured_catalog(stream, sync_mode=SyncMode.full_refresh)
        else:
            configured_catalog = create_configured_catalog(stream, sync_mode=SyncMode.incremental)

        for message in self.source.read(self.config, configured_catalog, state):
            if message.type == Type.RECORD:
                output = self._handle_record(message.record, get_defined_id(stream, message.record.data))
                if output:
                    yield output
            elif message.type is Type.STATE and message.state:
                self.last_state = message.state
