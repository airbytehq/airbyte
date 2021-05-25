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

from typing import Dict

from normalization import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer


class TableNameRegistry:
    """
    A registry object that records table names being used during processing.

    This registry helps on detecting naming conflicts/collisions and how to resolve them.
    """

    def __init__(self, destination_type: DestinationType):
        """
        @param destination_type is the destination type of warehouse
        """
        self.destination_type: DestinationType = destination_type
        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(destination_type)
        self.registry: Dict[str, Dict[str, str]] = {}

    def merge_table_registry(self, local_registry: "TableNameRegistry") -> "TableNameRegistry":
        new_registry = local_registry.registry
        for schema in new_registry:
            if len(new_registry[schema]) > 0:
                if schema not in self.registry:
                    self.registry[schema] = {}
                for table_name in new_registry[schema]:
                    if table_name not in self.registry[schema]:
                        self.registry[schema][table_name] = new_registry[schema][table_name]
                    else:
                        raise KeyError(f"Duplicate table {table_name} in schema {schema}")
        return self

    def contains(self, schema: str, table_name: str) -> bool:
        """
        Check if schema . table_name already exists in:
         - "global" tables_registry: recording all produced schema/table from previously processed streams.
         - "local" local_registry: recording all produced schema/table from the current stream being processed.

        Note, we avoid side-effets modifications to registries and perform only read operations here...
        """
        return schema in self.registry and table_name in self.registry[schema]

    def add_table(self, file_name: str, schema: str, table_name: str):
        if self.contains(schema, table_name):
            raise KeyError(f"Duplicate table {table_name} in schema {schema}")
        if schema not in self.registry:
            self.registry[schema] = {}
        self.registry[schema][table_name] = file_name
