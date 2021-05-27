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
from typing import Dict, List, Sequence, Tuple

from normalization import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer

# minimum length of parent name used for nested streams
MINIMUM_PARENT_LENGTH = 10


class TableNameRegistry:
    """
    A registry object that records table names being used during the run

    This registry helps detecting naming conflicts/collisions and how to resolve them.

    First, we collect all schema/stream_name/json_path listed in the catalog to detect any collisions, whether it is from:
     - table naming: truncated stream name could conflict with each other within the same destination schema
     - file naming: dbt use a global registry of file names without considering schema, so two tables with the same name in different schema
     is valid but dbt would fail to distinguish them. Thus, the file needs should be unique within a dbt project (for example,
     by adding the schema name to the file name when such collision occurs?)

     To do so, we build list of "simple" names without dealing with any collisions.
     Next, we check if/when we encounter such naming conflicts. They usually happen when destination require a certain naming convention
     with a limited number of characters, thus, we have to end up truncating names and creating collisions.

     In those cases, we resolve collisions using a more complex naming scheme using a suffix generated from hash of full names to make
     them short and unique (but hard to remember/use).
    """

    def __init__(self, destination_type: DestinationType):
        """
        @param destination_type is the destination type of warehouse
        """
        self.destination_type: DestinationType = destination_type
        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(destination_type)
        # all_files is a mapping of { file -> [ (intermediate_schema, schema, json_path, stream_name, table) ] }
        self.all_files: Dict[str, List[Tuple[str, str, List[str], str, str]]] = {}
        # all_tables is a mapping of { schema.table -> [ (intermediate_schema, schema, json_path, stream_name, table) ] }
        self.all_tables: Dict[str, List[Tuple[str, str, List[str], str, str]]] = {}
        # Registry is the collision free mapping of schema json_path of the stream to the names that should be used
        # { schema.json_path.stream_name -> [schema, table, file] }
        self.registry: Dict[str, List[str]] = {}

    def register_table(self, intermediate_schema: str, schema: str, stream_name: str, json_path: List[str]):
        """
        Record usages of simple table and file names used by each stream (top level and nested) in both
        intermediate_schema and schema.

        After going through all streams and sub-streams, we'll be able to find if any collisions are present within
        this catalog.
        """
        intermediate_schema = self.name_transformer.normalize_schema_name(intermediate_schema, False, False)
        schema = self.name_transformer.normalize_schema_name(schema, False, False)
        table_name = self.get_simple_table_name(json_path)
        # Record file name usage
        if table_name not in self.all_files:
            self.all_files[table_name] = []
        self.all_files[table_name].append((intermediate_schema, schema, json_path, stream_name, table_name))
        # Record schema & table name usage
        key = self.get_table_key(schema, table_name)
        if key not in self.all_tables:
            self.all_tables[key] = []
        self.all_tables[key].append((intermediate_schema, schema, json_path, stream_name, table_name))

    def get_simple_table_name(self, json_path: List[str]) -> str:
        """
        Generates a simple table name, possibly in collisions within this catalog because of truncation
        """
        return self.name_transformer.normalize_table_name("_".join(json_path))

    def resolve_names(self) -> List[List[Sequence[str]]]:
        """
        Build a collision free registry from all schema/stream_name/json_path collected so far.
        """
        resolved_keys = []
        # deal with table name collisions within the same schema first.
        # file name should be equal to table name here
        table_count = 0
        for key in self.all_tables:
            values = self.all_tables[key]
            if len(values) == 1:
                table_count += 1
                value = values[0]
                # no collisions
                intermediate_schema = value[0]
                schema = value[1]
                json_path = value[2]
                stream_name = value[3]
                table_name = value[4]
                self.registry[self.get_registry_key(intermediate_schema, json_path, stream_name)] = [
                    intermediate_schema,
                    table_name,
                    table_name,
                ]
                self.registry[self.get_registry_key(schema, json_path, stream_name)] = [schema, table_name, table_name]
            else:
                # collisions
                for value in values:
                    table_count += 1
                    intermediate_schema = value[0]
                    schema = value[1]
                    json_path = value[2]
                    stream_name = value[3]
                    table_name = self.get_hashed_table_name(schema, json_path, stream_name, value[4])
                    resolved_keys.append([schema, value[4], json_path, table_name])
                    self.registry[self.get_registry_key(intermediate_schema, json_path, stream_name)] = [
                        intermediate_schema,
                        table_name,
                        table_name,
                    ]
                    self.registry[self.get_registry_key(schema, json_path, stream_name)] = [schema, table_name, table_name]
        registry_size = len(self.registry)
        assert (table_count * 2) == registry_size, f"Mismatched number of tables {table_count} vs {registry_size} being resolved"
        # deal with file name collisions across schemas and update the file name to use in the registry when necessary
        file_count = 0
        for table_name in self.all_files:
            values = self.all_files[table_name]
            if len(values) > 1:
                for value in values:
                    file_count += 1
                    intermediate_schema = value[0]
                    schema = value[1]
                    json_path = value[2]
                    stream_name = value[3]
                    table_name = self.registry[self.get_registry_key(schema, json_path, stream_name)][1]
                    file_name = self.resolve_file_name(intermediate_schema, value[4])
                    self.registry[self.get_registry_key(intermediate_schema, json_path, stream_name)] = [
                        intermediate_schema,
                        table_name,
                        file_name,
                    ]
                    file_name = self.resolve_file_name(schema, value[4])
                    self.registry[self.get_registry_key(schema, json_path, stream_name)] = [schema, table_name, file_name]
            else:
                file_count += 1
        assert (file_count * 2) == registry_size, f"Mismatched number of tables {file_count} vs {registry_size} being resolved"
        return resolved_keys

    def get_hashed_table_name(self, schema: str, json_path: List[str], stream_name: str, table_name: str) -> str:
        """
        Generates a unique table name to avoid collisions within this catalog.
        This is using a hash of full names but it is hard to use and remember, so this should be done rarely...
        We'd prefer to use "simple" names instead as much as possible.
        """
        if len(json_path) == 1:
            # collisions on a top level stream name, add a hash of schema + stream name to the (truncated?) table name to make it unique
            result = self.name_transformer.normalize_table_name(f"{stream_name}_{hash_json_path([schema] + json_path)}")
        else:
            # collisions on a nested sub-stream
            result = self.name_transformer.normalize_table_name(
                get_nested_hashed_table_name(self.name_transformer, schema, json_path, stream_name), False, False
            )
        return result

    def get_table_key(self, schema: str, table_name: str) -> str:
        """
        Build the key string used to index in all_tables field
        """
        return f"{self.name_transformer.normalize_schema_name(schema, False, False)}.{self.name_transformer.normalize_table_name(table_name, False, False)}"

    def get_registry_key(self, schema: str, json_path: List[str], stream_name: str) -> str:
        """
        Build the key string used to index the registry
        """
        return ".".join([schema, "_".join(json_path), stream_name]).lower()

    def resolve_file_name(self, schema: str, table_name: str) -> str:
        """
        We prefer to use file_name = table_name when possible...

        When a catalog has ambiguity, we have to fallback and use schema in the file name too
        (which might increase a risk of truncate operation and thus collisions that we solve by adding a hash of the full names)
        """
        if len(self.all_files[table_name]) == 1:
            # no collisions on file naming
            return table_name
        else:
            max_length = self.name_transformer.get_name_max_length()
            # if schema . table fits into the destination, we use this naming convention
            if len(schema) + len(table_name) + 1 < max_length:
                return f"{schema}_{table_name}"
            else:
                # we have to make sure our filename is unique, use hash of full name
                return self.name_transformer.normalize_table_name(f"{schema}_{table_name}_{hash_name(schema + table_name)}")

    def get_schema_name(self, schema: str, json_path: List[str], stream_name: str):
        """
        Return the schema name from the registry that should be used for this combination of schema/json_path_to_substream
        """
        key = self.get_registry_key(schema, json_path, stream_name)
        if key in self.registry:
            return self.name_transformer.normalize_schema_name(self.registry[key][0], False, False)
        else:
            raise KeyError(f"Registry does not contain an entry for {schema} {json_path}")

    def get_table_name(self, schema: str, json_path: List[str], stream_name: str, suffix: str):
        """
        Return the table name from the registry that should be used for this combination of schema/json_path_to_substream
        """
        key = self.get_registry_key(schema, json_path, stream_name)
        if key in self.registry:
            table_name = self.registry[key][1]
        else:
            raise KeyError(f"Registry does not contain an entry for {schema} {json_path} {stream_name}")
        if suffix:
            norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
        else:
            norm_suffix = ""
        return self.name_transformer.normalize_table_name(f"{table_name}{norm_suffix}", False, False)

    def get_file_name(self, schema: str, json_path: List[str], stream_name: str, suffix: str):
        """
        Return the file name from the registry that should be used for this combination of schema/json_path_to_substream
        """
        key = self.get_registry_key(schema, json_path, stream_name)
        if key in self.registry:
            file_name = self.registry[key][2]
        else:
            raise KeyError(f"Registry does not contain an entry for {schema} {json_path} {stream_name}")
        if suffix:
            norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
        else:
            norm_suffix = ""
        return self.name_transformer.normalize_table_name(f"{file_name}{norm_suffix}", False, False)


def hash_json_path(json_path: List[str]) -> str:
    return hash_name("&airbyte&".join(json_path))


def hash_name(input: str) -> str:
    h = hashlib.sha1()
    h.update(input.encode("utf-8").lower())
    return h.hexdigest()[:3]


def get_nested_hashed_table_name(name_transformer: DestinationNameTransformer, schema: str, json_path: List[str], child: str) -> str:
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
    parent = "_".join(json_path[:-1])
    max_length = name_transformer.get_name_max_length()
    json_path_hash = hash_json_path([schema] + json_path)
    norm_parent = parent if not parent else name_transformer.normalize_table_name(parent, False, False)
    norm_child = name_transformer.normalize_table_name(child, False, False)
    min_parent_length = min(MINIMUM_PARENT_LENGTH, len(norm_parent))

    # no parent
    if not parent:
        raise RuntimeError("There is no nested table names without parents")
    # if everything fits without truncation, don't truncate anything
    elif (len(norm_parent) + len(json_path_hash) + len(norm_child) + 2) < max_length:
        return f"{norm_parent}_{json_path_hash}_{norm_child}"
    # if everything fits except for the parent, just truncate the parent (still guarantees parent is of length min_parent_length)
    elif (min_parent_length + len(json_path_hash) + len(norm_child) + 2) < max_length:
        max_parent_length = max_length - len(json_path_hash) - len(norm_child) - 2
        return f"{norm_parent[:max_parent_length]}_{json_path_hash}_{norm_child}"
    # otherwise first truncate parent to the minimum length and middle truncate the child too
    else:
        norm_child_max_length = max_length - len(json_path_hash) - 2 - min_parent_length
        trunc_norm_child = name_transformer.truncate_identifier_name(norm_child, norm_child_max_length)
        return f"{norm_parent[:min_parent_length]}_{json_path_hash}_{trunc_norm_child}"
