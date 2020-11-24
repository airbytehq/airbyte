""" MIT License

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

import inspect
import json
import pkgutil
from abc import ABC
from datetime import datetime
from typing import Tuple, Dict

from airbyte_protocol import AirbyteStream, AirbyteRecordMessage


class ResourceSchemaLoader:
    """ JSONSchema loader from package resources
    """
    def get_schema(self, name):
        raw_schema = json.loads(
            pkgutil.get_data(self.__class__.__module__.split(".")[0],
                             f"schemas/{name}.json"))
        return raw_schema


class URLSchemaLoader:
    """ JSONSchema loader from URL
    """
    def get_schema(self, name):
        raise NotImplementedError


class BaseClient(ABC):
    """ Base client for API
    """
    schema_loader_class = ResourceSchemaLoader

    def __init__(self, **kwargs):
        self._schema_loader = self.schema_loader_class()
        self._stream_methods = self._enumerate_methods()

    def _enumerate_methods(self) -> Dict[str, callable]:
        """ Detect available streams and return mapping
        """
        prefix = 'stream__'
        mapping = {}
        methods = inspect.getmembers(self.__class__,
                                     predicate=inspect.isfunction)
        for name, method in methods:
            if name.startswith(prefix):
                mapping[name[len(prefix):]] = method

        return mapping

    def read_stream(self, stream):
        """ Yield records from stream
        """
        method = self._stream_methods.get(stream)
        if not method:
            raise ValueError(
                f"Client does not know how to read stream `{stream.name}`")

        for message in method():
            now = int(datetime.now().timestamp()) * 1000
            yield AirbyteRecordMessage(stream=stream.name, data=message,
                                       emitted_at=now)

    @property
    def streams(self):
        """ List of available streams
        """
        for name, method in self._stream_methods.items():
            yield AirbyteStream(name,
                                schema=self._schema_loader.get_schema(name))

    def health_check(self) -> Tuple[bool, str]:
        """ Check if service is up and running
        """
        raise NotImplementedError
