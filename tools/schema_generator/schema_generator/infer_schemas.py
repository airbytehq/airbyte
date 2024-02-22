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

import json
import os
import sys

import genson.schema.strategies as strategies
from airbyte_cdk.models import AirbyteMessage, Type
from genson import SchemaBuilder
from genson.schema.strategies.object import Object


class NoRequiredObj(Object):
    """
    This class has Object behaviour, but it does not generate "required[]" fields
    every time it parses object. So we dont add unnecessary extra field.
    """

    def to_schema(self):
        schema = super(Object, self).to_schema()
        schema["type"] = "object"
        if self._properties:
            schema["properties"] = self._properties_to_schema(self._properties)
        if self._pattern_properties:
            schema["patternProperties"] = self._properties_to_schema(self._pattern_properties)

        schema["additionalProperties"] = True
        return schema


class NoRequiredSchemaBuilder(SchemaBuilder):
    EXTRA_STRATEGIES = (NoRequiredObj,)

    def __init__(self):
        super().__init__(schema_uri="http://json-schema.org/draft-07/schema#")


def infer_schemas():
    default_folder = os.path.join(os.getcwd(), "schemas")
    if not os.path.exists(default_folder):
        os.mkdir(default_folder)

    builders = {}
    for line in sys.stdin:
        message = AirbyteMessage.parse_raw(line)
        if message.type == Type.RECORD:
            stream_name = message.record.stream
            if stream_name not in builders:
                builder = NoRequiredSchemaBuilder()
                builders[stream_name] = builder
            else:
                builder = builders[stream_name]
            builder.add_object(message.record.data)
    for stream_name, builder in builders.items():
        schema = builder.to_schema()
        output_file_name = os.path.join(default_folder, stream_name + ".json")
        with open(output_file_name, "w") as outfile:
            json.dump(schema, outfile, indent=2, sort_keys=True)
