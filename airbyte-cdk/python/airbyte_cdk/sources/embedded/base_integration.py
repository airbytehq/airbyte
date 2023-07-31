from abc import ABC, abstractmethod
from typing import Generic, Iterable, List, Optional, TypeVar

from airbyte_cdk.connector import TConfig
from airbyte_cdk.sources.source import TState
from airbyte_protocol.models import AirbyteRecordMessage, AirbyteStateMessage, Type, SyncMode

from airbyte_cdk.sources.embedded.catalog import create_configured_catalog, get_stream_names, retrieve_catalog, get_stream
from airbyte_cdk.sources.embedded.tools import get_defined_id
from airbyte_cdk.sources.embedded.runner import SourceRunner

TOutput = TypeVar("TOutput")


class BaseEmbeddedIntegration(ABC, Generic[TConfig, TState, TOutput]):
    def __init__(self, source: SourceRunner[TConfig, TState], config: TConfig):
        self.source = source
        self.config = config

        self.last_state: Optional[AirbyteStateMessage] = None

    @abstractmethod
    def _handle_record(self, record: AirbyteRecordMessage, id: Optional[str]) -> Optional[TOutput]:
        """
        Turn an Airbyte record into the appropriate output type for the integration.
        """
        pass

    def _load_data(self, stream: str, state: Optional[TState]) -> Iterable[TOutput]:
        catalog = self.source.discover(self.config)
        if not state:
            configured_catalog = create_configured_catalog([stream], catalog, sync_mode=SyncMode.full_refresh)
        else:
            configured_catalog = create_configured_catalog([stream], catalog, sync_mode=SyncMode.incremental)

        stream = get_stream(catalog, stream)

        for message in self.source.read(self.config, configured_catalog, state):
            if message.type == Type.RECORD:
                output = self._handle_record(message.record, get_defined_id(stream, message.record.data))
                if output:
                    yield output
            elif message.type is Type.STATE and message.state:
                self.last_state = message.state
