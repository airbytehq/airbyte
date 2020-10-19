import json
import pkgutil
from dataclasses import dataclass
from typing import Generator

from .models import AirbyteCatalog, AirbyteMessage


class AirbyteSpec(object):
    @staticmethod
    def from_file(file):
        with open(file) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def __init__(self, spec_string):
        self.spec_string = spec_string


class AirbyteCheckResponse(object):
    def __init__(self, successful, field_to_error):
        self.successful = successful
        self.field_to_error = field_to_error


@dataclass
class ConfigContainer:
    raw_config: object
    rendered_config: object
    raw_config_path: str
    rendered_config_path: str


class Integration(object):
    def __init__(self):
        pass

    def spec(self, logger) -> AirbyteSpec:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split('.')[0], 'spec.json')
        # we need to output a spec on a single line
        flattened_json = json.dumps(json.loads(raw_spec))
        return AirbyteSpec(flattened_json)

    def read_config(self, config_path):
        with open(config_path, 'r') as file:
            contents = file.read()
        return json.loads(contents)

    # can be overridden to change an input file config
    def transform_config(self, raw_config):
        return raw_config

    def write_config(self, config_object, path):
        with open(path, 'w') as fh:
            fh.write(json.dumps(config_object))

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        raise Exception("Not Implemented")

    def discover(self, logger, config_container) -> AirbyteCatalog:
        raise Exception("Not Implemented")


class Source(Integration):
    def __init__(self):
        super().__init__()

    # Iterator<AirbyteMessage>
    def read(self, logger, config_container, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        raise Exception("Not Implemented")


class Destination(Integration):
    def __init__(self):
        super().__init__()
