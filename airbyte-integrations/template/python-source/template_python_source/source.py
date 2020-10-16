import pkgutil
import time
from typing import Generator

from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import AirbyteRecordMessage
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteStateMessage
from airbyte_protocol import Source


class TemplatePythonSource(Source):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        logger.info(f'Checking configuration ({config_container.rendered_config_path})...')
        return AirbyteCheckResponse(True, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        logger.info(f'Discovering ({config_container.rendered_config_path})...')
        return AirbyteCatalog.from_json(pkgutil.get_data(__name__, 'catalog.json'))

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        logger.info(f'Reading ({config_container.rendered_config_path}, {catalog_path}, {state})...')

        message = AirbyteRecordMessage(
            stream='love_airbyte',
            data={'love': True},
            emitted_at=int(time.time() * 1000))
        yield AirbyteMessage(type='RECORD', record=message)

        state = AirbyteStateMessage(data={'love_cursor': 'next_version'})
        yield AirbyteMessage(type='STATE', state=state)
