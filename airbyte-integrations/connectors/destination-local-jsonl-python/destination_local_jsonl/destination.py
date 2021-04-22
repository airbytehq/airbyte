from typing import Iterable, Mapping

from airbyte_protocol import AirbyteMessage, ConfiguredAirbyteCatalog, AirbyteConnectionStatus
from base_python import Destination, AirbyteLogger


class DestinationLocalJsonL(Destination):
    def check(self, logger: AirbyteLogger, config: Mapping[str, any]) -> AirbyteConnectionStatus:
        """

        :param logger:
        :param config:
        :return:
        """

    
    def write(self, logger: AirbyteLogger, config: Mapping[str, any], configured_catalog: ConfiguredAirbyteCatalog) -> Iterable[AirbyteMessage]:
        # stdin =
        pass
