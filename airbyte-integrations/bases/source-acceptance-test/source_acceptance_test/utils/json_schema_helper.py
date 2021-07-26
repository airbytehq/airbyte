#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from collections import defaultdict
from functools import reduce
from typing import Any, List, Mapping, MutableMapping, Optional, Set

import pendulum
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream


class CatalogField:
    """Field class to represent cursor/pk fields"""

    def __init__(self, schema: Mapping[str, Any], path: List[str]):
        self.schema = schema
        self.path = path
        self.formats = self._detect_formats()

    def _detect_formats(self) -> Set[str]:
        """Extract set of formats/types for this field"""
        format_ = []
        try:
            format_ = self.schema.get("format", self.schema["type"])
            if not isinstance(format_, List):
                format_ = [format_]
        except KeyError:
            pass
        return set(format_)

    def _parse_value(self, value: Any) -> Any:
        """Do actual parsing of the serialized value"""
        if self.formats.intersection({"datetime", "date-time", "date"}):
            if value is None and "null" not in self.formats:
                raise ValueError(f"Invalid field format. Value: {value}. Format: {self.formats}")
            # handle beautiful MySQL datetime, i.e. NULL datetime
            if value.startswith("0000-00-00"):
                value = value.replace("0000-00-00", "0001-01-01")
            return pendulum.parse(value)
        return value

    def parse(self, record: Mapping[str, Any], path: Optional[List[str]] = None) -> Any:
        """Extract field value from the record and cast it to native type"""
        path = path or self.path
        value = reduce(lambda data, key: data[key], path, record)
        return self._parse_value(value)


class JsonSchemaHelper:
    def __init__(self, schema):
        self._schema = schema

    def get_ref(self, path: List[str]):
        node = self._schema
        for segment in path.split("/")[1:]:
            node = node[segment]
        return node

    def get_property(self, path: List[str]) -> Mapping[str, Any]:
        node = self._schema
        for segment in path:
            if "$ref" in node:
                node = self.get_ref(node["$ref"])
            node = node["properties"][segment]
        return node

    def field(self, path: List[str]) -> CatalogField:
        return CatalogField(schema=self.get_property(path), path=path)


class StreamHelper:
    def __init__(self, stream: ConfiguredAirbyteStream):
        self._stream = stream
        self._json_helper = JsonSchemaHelper(stream.stream.json_schema)

    @property
    def primary_key(self) -> Optional[List[CatalogField]]:
        pks = self._stream.primary_key or self._stream.stream.source_defined_primary_key
        if pks:
            return [self._json_helper.field(pk) for pk in pks]

    @property
    def cursor_field(self) -> Optional[CatalogField]:
        if self._stream.cursor_field:
            return self._json_helper.field(self._stream.cursor_field)

    @staticmethod
    def group_by_keys(records: List[MutableMapping[str, Any]], keys: List[CatalogField]):
        result = defaultdict(list)
        for record in records:
            key = tuple([key_field.parse(record) for key_field in keys])
            result[key].append(record)

        return result


class CatalogHelper:
    def __init__(self, catalog: ConfiguredAirbyteCatalog):
        self._catalog = catalog

    def stream(self, name: str) -> Optional[StreamHelper]:
        for s in self._catalog.streams:
            if s.stream.name == name:
                return StreamHelper(s)
