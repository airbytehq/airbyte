#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional

from airbyte_cdk.connector import TConfig
from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.source import TState


class SourceRunner(ABC, Generic[TConfig, TState]):
    @abstractmethod
    def discover(self, config: TConfig) -> AirbyteCatalog:
        pass

    @abstractmethod
    def read(self, config: TConfig, catalog: ConfiguredAirbyteCatalog, state: Optional[TState]) -> Iterable[AirbyteMessage]:
        pass
