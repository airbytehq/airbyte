
from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional
from logging import Logger

from airbyte_cdk.sources.source import TState, Source
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteCatalog, AirbyteMessage
from airbyte_cdk.connector import TConfig


class SourceRunner(ABC, Generic[TConfig, TState]):
    @abstractmethod
    def discover(self, config: TConfig) -> AirbyteCatalog:
        pass

    @abstractmethod
    def read(self, config: TConfig, catalog: ConfiguredAirbyteCatalog, state: Optional[TState]) -> Iterable[AirbyteMessage]:
        pass
