"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import pkgutil
from dataclasses import dataclass
from typing import Generator

from .models import AirbyteCatalog, AirbyteMessage, ConnectorSpecification

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

    def spec(self, logger) -> ConnectorSpecification:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split('.')[0], 'spec.json')
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

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
