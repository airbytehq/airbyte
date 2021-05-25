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

import hashlib
from typing import Dict, List

from normalization import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer

# minimum length of parent name used for nested streams
MINIMUM_PARENT_LENGTH = 10


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

    def register_stream(self, schema: str, stream_name: str, suffix: str, json_path: List[str]) -> (str, str):
        table_name = self.generate_new_table_name(schema, stream_name, suffix, json_path)
        file_name = self.get_file_name(schema, stream_name, table_name)
        self.add_table(schema, table_name, file_name)
        return table_name, file_name

    def generate_new_table_name(self, schema: str, stream_name: str, suffix: str, json_path: List[str]) -> str:
        """
        Generates a new table name that is not registered in the schema yet (based on stream_name)
        """
        if suffix:
            norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
        else:
            norm_suffix = ""
        if len(json_path) == 1:
            new_table_name = self.name_transformer.normalize_table_name(f"{stream_name}{norm_suffix}", False, True)
        else:
            new_table_name = get_nested_table_name(self.name_transformer, "_".join(json_path[:-1]), stream_name, norm_suffix, json_path)
        new_table_name = self.name_transformer.normalize_table_name(new_table_name, False, False)
        if self.contains(schema, new_table_name):
            # Check if new_table_name already exists. If yes, then add hash of the stream name to it
            if len(json_path) == 1:
                new_table_name = self.name_transformer.normalize_table_name(
                    f"{stream_name}{norm_suffix}_{hash_name(stream_name)}", False, True
                )
            else:
                new_table_name = get_nested_table_name(
                    self.name_transformer, "_".join(json_path[:-1]), stream_name, f"{norm_suffix}_{hash_name(stream_name)}", json_path
                )
            new_table_name = self.name_transformer.normalize_table_name(new_table_name, False, False)
            if self.contains(schema, new_table_name):
                raise ValueError(
                    f"Conflict: Table name {new_table_name} in schema {schema} already exists! (is there a hashing collision or duplicate streams?)"
                )
        return new_table_name

    def get_file_name(self, schema_name: str, stream_name: str, table_name: str) -> str:
        """
        File names need to match the ref() macro returned in the ref_table function.
        Note that dbt uses only the file names to generate internal model.

        Use a hash of full schema + stream name (i.e. namespace + stream name) to dedup tables.
        This hash avoids tables with the same name (possibly very long) and different schemas.
        """
        full_lower_name = schema_name + "_" + stream_name
        full_lower_name = full_lower_name.lower()
        return self.name_transformer.normalize_table_name(f"{table_name}_{hash_name(full_lower_name)}", False, False)

    def add_table(self, schema: str, table_name: str, file_name: str):
        if self.contains(schema, table_name):
            raise KeyError(f"Duplicate table {table_name} in schema {schema}")
        if schema not in self.registry:
            self.registry[schema] = {}
        self.registry[schema][table_name] = file_name


def hash_json_path(json_path: List[str]) -> str:
    return hash_name("&airbyte&".join(json_path))


def hash_name(input: str) -> str:
    h = hashlib.sha1()
    h.update(input.encode("utf-8"))
    return h.hexdigest()[:3]


def get_nested_table_name(name_transformer: DestinationNameTransformer, parent: str, child: str, suffix: str, json_path: List[str]) -> str:
    """
    In normalization code base, we often have to deal with naming for tables, combining informations from:
    - parent table: to denote where a table is extracted from (in case of nesting)
    - child table: in case of nesting, the field name or the original stream name
    - extra suffix: normalization is done in multiple transformation steps, each may need to generate separate tables,
    so we can add a suffix to distinguish the different transformation steps of a pipeline.
    - json path: in terms of parent and nested field names in order to reach the table currently being built

    All these informations should be included (if possible) in the table naming for the user to (somehow) identify and
    recognize what data is available there.
    """
    if suffix:
        norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
    else:
        norm_suffix = ""
    max_length = name_transformer.get_name_max_length()
    json_path_hash = hash_json_path(json_path)
    norm_parent = parent if not parent else name_transformer.normalize_table_name(parent, False, False)
    norm_child = name_transformer.normalize_table_name(child, False, False)
    min_parent_length = min(MINIMUM_PARENT_LENGTH, len(norm_parent))

    # no parent
    if not parent:
        return name_transformer.truncate_identifier_name(f"{norm_child}{norm_suffix}")
    # if everything fits without truncation, don't truncate anything
    elif (len(norm_parent) + len(json_path_hash) + len(norm_child) + len(norm_suffix) + 2) < max_length:
        return f"{norm_parent}_{json_path_hash}_{norm_child}{norm_suffix}"
    # if everything fits except for the parent, just truncate the parent (still guarantees parent is of length min_parent_length)
    elif (min_parent_length + len(json_path_hash) + len(norm_child) + len(norm_suffix) + 2) < max_length:
        max_parent_length = max_length - len(json_path_hash) - len(norm_child) - len(norm_suffix) - 2
        return f"{norm_parent[:max_parent_length]}_{json_path_hash}_{norm_child}{norm_suffix}"
    # otherwise first truncate parent to the minimum length and middle truncate the child too
    else:
        norm_child_max_length = max_length - len(json_path_hash) - len(norm_suffix) - 2 - min_parent_length - 1
        trunc_norm_child = name_transformer.truncate_identifier_name(norm_child, norm_child_max_length)
        return f"{norm_parent[:min_parent_length]}_{json_path_hash}_{trunc_norm_child}{norm_suffix}"
