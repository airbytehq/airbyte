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


from functools import reduce
from typing import Any, List, Set

import pendulum


class JsonSchemaHelper:
    def __init__(self, schema):
        self._schema = schema

    def get_ref(self, path):
        node = self._schema
        for segment in path.split("/")[1:]:
            node = node[segment]
        return node

    def get_property(self, path: List[str]):
        node = self._schema
        for segment in path:
            if "$ref" in node:
                node = self.get_ref(node["$ref"])
            node = node["properties"][segment]
        return node

    def get_format_for_key_path(self, path: List[str]) -> Set[str]:
        format_ = []
        try:
            field = self.get_property(path)
            format_ = field.get("format", field["type"])
            if not isinstance(format_, List):
                format_ = [format_]
        except KeyError:
            pass
        return set(format_)

    def get_cursor_value(self, record, cursor_path):
        type_ = self.get_format_for_key_path(path=cursor_path)
        value = reduce(lambda data, key: data[key], cursor_path, record)
        return self.parse_value(value, type_)

    @staticmethod
    def parse_value(value: Any, format_: Set[str]):
        if format_.intersection({"datetime", "date-time"}):
            if value is None and "null" not in format_:
                raise ValueError(f"Invalid field format. Value: {value}. Format: {format_}")
            return pendulum.parse(value)
        return value

    def get_state_value(self, state, cursor_path):
        format_ = self.get_format_for_key_path(path=cursor_path)
        value = state[cursor_path[-1]]
        return self.parse_value(value, format_)
