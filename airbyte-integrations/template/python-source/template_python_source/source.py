import datetime
import json
import pkgutil
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

    def spec(self, logger) -> AirbyteSpec:
        logger.info('Getting spec...')
        return AirbyteSpec.from_file('spec.json')

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        logger.info(f'Checking configuration ({config_container.rendered_config_path})...')
        return AirbyteCheckResponse(True, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        logger.info(f'Discovering ({config_container.rendered_config_path})...')
        return AirbyteCatalog(pkgutil.get_data(__name__, 'catalog.json'))

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        logger.info(f'Reading ({config_container.rendered_config_path}, {catalog_path}, {state})...')

        record = AirbyteRecordMessage(
            stream='love_airbyte',
            data=json.dumps({'love': True}),
            emitted_at=int(datetime.now().timestamp()) * 1000)
        yield AirbyteMessage(type="RECORD", record=record)

        state = AirbyteStateMessage(data=json.dumps({'next_love': 'next_version'}))
        yield AirbyteMessage(type="STATE", state=state)
