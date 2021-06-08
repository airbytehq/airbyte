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

from airbyte_cdk.models import AirbyteMessage, Type
from genson import SchemaBuilder
from genson.schema.strategies.object import Object


def to_schema(self):
    """
    Dirty override.
    THis is a stripped native Object.to_schema method.
    The library does no provide a way to
    avoid "required = [a,b,c]" in json schema within some parameter
    in `SchemaBuilder` constructor or this need investigation.
    So the dirty fix is to strip original method
    and not to add unwanted extra field `required`.
    Without further recursive looping over document and deleting this field
    I just do not create it.
    """
    schema = super(Object, self).to_schema()
    schema["type"] = "object"
    if self._properties:
        schema["properties"] = self._properties_to_schema(self._properties)
    if self._pattern_properties:
        schema["patternProperties"] = self._properties_to_schema(self._pattern_properties)
    return schema


Object.to_schema = to_schema


data = sys.stdin.readlines()

default_folder = os.path.join(os.getcwd(), "_schemas")
if not os.path.exists(default_folder):
    os.mkdir(default_folder)

messages = [AirbyteMessage.parse_raw(line) for line in data]
record_messages = [i for i in messages if i.type == Type.RECORD]
builders = {}  # "stream_name": builder_instance, "stream_name2: builder_instance2...}

for record in record_messages:
    stream_name = record.record.stream
    if stream_name not in builders:
        builder = SchemaBuilder()
        builders[stream_name] = builder
    else:
        builder = builders[stream_name]
    builder.add_object(record.record.data)

for stream_name, builder in builders.items():
    schema = builder.to_schema()
    output_file_name = os.path.join(default_folder, stream_name + ".json")
    with open(output_file_name, "w") as outfile:
        json.dump(schema, outfile, indent=2)
