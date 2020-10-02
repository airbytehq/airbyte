from integration import Integration

from integration import AirbyteMessage
from typing import Generator


class Source(Integration):
    def __init__(self):
        pass

    # Iterator<AirbyteMessage>
    def read(self, config_object, rendered_config_path, state=None) -> Generator[AirbyteMessage, None, None]:
        raise Exception("Not Implemented")
