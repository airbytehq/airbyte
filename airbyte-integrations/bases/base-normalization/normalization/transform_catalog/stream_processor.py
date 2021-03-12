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

import hashlib
import os
from typing import Dict, List, Optional, Set, Tuple

from airbyte_protocol.models.airbyte_protocol import DestinationSyncMode, SyncMode
from jinja2 import Template
from normalization.destination_type import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer
from normalization.transform_catalog.utils import (
    is_airbyte_column,
    is_array,
    is_boolean,
    is_combining_node,
    is_integer,
    is_number,
    is_object,
    is_simple_property,
    is_string,
    jinja_call,
)

# minimum length of parent name used for nested streams
MINIMUM_PARENT_LENGTH = 10


class StreamProcessor(object):
    """
    Takes as input an Airbyte Stream as described in the (configured) Airbyte Catalog's Json Schema.
    Associated input raw data is expected to be stored in a staging area table.

    This processor generates SQL models to transform such a stream into a final table in the destination schema.
    This is done by generating a DBT pipeline of transformations (multiple SQL models queries) that may be materialized
    in the intermediate schema "raw_schema" (changing the dbt_project.yml settings).
    The final output data should be written in "schema".

    The pipeline includes transformations such as:
    - Parsing a JSON blob column and extracting each field property in its own SQL column
    - Casting each SQL column to the proper JSON data type
    - Generating an artificial (primary key) ID column based on the hashing of the row

    If any nested columns are discovered in the stream, a JSON blob SQL column is created in the top level parent stream
    and a new StreamProcessor instance will be spawned for each children substreams. These Sub-Stream Processors are then
    able to generate models to parse and extract recursively from its parent StreamProcessor model into separate SQL tables
    the content of that JSON blob SQL column.
    """

    def __init__(
        self,
        stream_name: str,
        destination_type: DestinationType,
        raw_schema: str,
        schema: str,
        source_sync_mode: SyncMode,
        destination_sync_mode: DestinationSyncMode,
        cursor_field: List[str],
        primary_key: List[List[str]],
        json_column_name: str,
        properties: Dict,
        tables_registry: Set[str],
        from_table: str,
    ):
        """
        See StreamProcessor.create()
        """
        self.stream_name: str = stream_name
        self.destination_type: DestinationType = destination_type
        self.raw_schema: str = raw_schema
        self.schema: str = schema
        self.source_sync_mode: SyncMode = source_sync_mode
        self.destination_sync_mode: DestinationSyncMode = destination_sync_mode
        self.cursor_field: List[str] = cursor_field
        self.primary_key: List[List[str]] = primary_key
        self.json_column_name: str = json_column_name
        self.properties: Dict = properties
        self.tables_registry: Set[str] = tables_registry
        self.from_table: str = from_table

        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(destination_type)
        self.json_path: List[str] = [stream_name]
        self.final_table_name: str = ""
        self.sql_outputs: Dict[str, str] = {}
        self.local_registry: Set[str] = set()
        self.parent: Optional["StreamProcessor"] = None
        self.is_nested_array: bool = False

    @staticmethod
    def create_from_parent(
        parent, child_name: str, json_column_name: str, properties: Dict, is_nested_array: bool, from_table: str
    ) -> "StreamProcessor":
        """
        @param parent is the Stream Processor that originally created this instance to handle a nested column from that parent table.

        @param json_column_name is the name of the column in the parent data table containing the json column to transform
        @param properties is the json schema description of this nested stream
        @param is_nested_array is a boolean flag specifying if the child is a nested array that needs to be extracted

        @param tables_registry is the global context recording all tables created so far
        @param from_table is the parent table to extract the nested stream from

        The child stream processor will create a separate table to contain the unnested data.
        """
        result = StreamProcessor.create(
            stream_name=child_name,
            destination_type=parent.destination_type,
            raw_schema=parent.raw_schema,
            schema=parent.schema,
            # Nested Streams don't inherit parents sync modes?
            source_sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
            cursor_field=[],
            primary_key=[],
            json_column_name=json_column_name,
            properties=properties,
            tables_registry=parent.tables_registry,
            from_table=from_table,
        )
        result.parent = parent
        result.is_nested_array = is_nested_array
        result.json_path = parent.json_path + [child_name]
        return result

    @staticmethod
    def create(
        stream_name: str,
        destination_type: DestinationType,
        raw_schema: str,
        schema: str,
        source_sync_mode: SyncMode,
        destination_sync_mode: DestinationSyncMode,
        cursor_field: List[str],
        primary_key: List[List[str]],
        json_column_name: str,
        properties: Dict,
        tables_registry: Set[str],
        from_table: str,
    ) -> "StreamProcessor":
        """
        @param stream_name of the stream being processed

        @param destination_type is the destination type of warehouse
        @param raw_schema is the name of the staging intermediate schema where to create internal tables/views
        @param schema is the name of the schema where to store the final tables where to store the transformed data

        @param source_sync_mode is describing how source are producing data
        @param destination_sync_mode is describing how destination should handle the new data batch
        @param cursor_field is the field to use to determine order of records
        @param primary_key is a list of fields to use as a (composite) primary key

        @param json_column_name is the name of the column in the raw data table containing the json column to transform
        @param properties is the json schema description of this stream

        @param tables_registry is the global context recording all tables created so far
        @param from_table is the table this stream is being extracted from originally
        """
        return StreamProcessor(
            stream_name,
            destination_type,
            raw_schema,
            schema,
            source_sync_mode,
            destination_sync_mode,
            cursor_field,
            primary_key,
            json_column_name,
            properties,
            tables_registry,
            from_table,
        )

    def process(self) -> List["StreamProcessor"]:
        """
        See description of StreamProcessor class.
        @return List of StreamProcessor to handle recursively nested columns from this stream
        """
        # Check properties
        if not self.properties:
            print(f"  Ignoring substream '{self.stream_name}' from {self.current_json_path()} because properties list is empty")
            return []

        column_names = self.extract_column_names()

        from_table = self.from_table
        # Transformation Pipeline for this stream
        from_table = self.add_to_outputs(self.generate_json_parsing_model(from_table, column_names), is_intermediate=True, suffix="ab1")
        from_table = self.add_to_outputs(self.generate_column_typing_model(from_table, column_names), is_intermediate=True, suffix="ab2")
        from_table = self.add_to_outputs(self.generate_id_hashing_model(from_table, column_names), is_intermediate=True, suffix="ab3")
        if self.destination_sync_mode.value == DestinationSyncMode.append_dedup.value:
            from_table = self.add_to_outputs(self.generate_dedup_record_model(from_table, column_names), is_intermediate=True, suffix="ab4")
            where_clause = "\nwhere _airbyte_row_num = 1"
            from_table = self.add_to_outputs(
                self.generate_scd_type_2_model(from_table, column_names) + where_clause, is_intermediate=False, suffix="scd"
            )
            where_clause = "\nwhere _airbyte_active_row = True"
            from_table = self.add_to_outputs(self.generate_final_model(from_table, column_names) + where_clause, is_intermediate=False)
            # TODO generate yaml file to dbt test final table where primary keys should be unique
        else:
            from_table = self.add_to_outputs(self.generate_final_model(from_table, column_names), is_intermediate=False)
        return self.find_children_streams(from_table, column_names)

    def extract_column_names(self) -> Dict[str, Tuple[str, str]]:
        """
        Generate a mapping of JSON properties to normalized SQL Column names, handling collisions and avoid duplicate names

        The mapped value to a field property is a tuple where:
         - the first value is the normalized "raw" column name
         - the second value is the normalized quoted column name to be used in jinja context
        """
        fields = []
        for field in self.properties.keys():
            if not is_airbyte_column(field):
                fields.append(field)
            if self.destination_sync_mode.value == DestinationSyncMode.append_dedup.value:
                # When deduping, some airbyte columns could be used as special cursor or primary key columns
                if field in self.cursor_field[0] or field in [f[0] for f in self.primary_key if len(f) == 1]:
                    if field not in fields:
                        fields.append(field)
        result = {}
        field_names = set()
        for field in fields:
            field_name = self.name_transformer.normalize_column_name(field, in_jinja=False)
            jinja_name = self.name_transformer.normalize_column_name(field, in_jinja=True)
            if field_name in field_names:
                # TODO handle column name duplicates or collisions deterministically in this stream
                for i in range(1, 1000):
                    field_name = self.name_transformer.normalize_column_name(f"{field}_{i}", in_jinja=False)
                    jinja_name = self.name_transformer.normalize_column_name(f"{field}_{i}", in_jinja=True)
                    if field_name not in field_names:
                        break
            field_names.add(field_name)
            result[field] = (field_name, jinja_name)
        return result

    def find_children_streams(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> List["StreamProcessor"]:
        """
        For each complex type properties, generate a new child StreamProcessor that produce separate child pipelines.
        The current stream/table is used as the parent from which to extract data from.
        """
        properties = self.properties
        children: List[StreamProcessor] = []
        for field in properties.keys():
            children_properties = None
            if is_airbyte_column(field):
                pass
            elif is_combining_node(properties[field]):
                # TODO: merge properties of all combinations
                pass
            elif "type" not in properties[field] or is_object(properties[field]["type"]):
                # properties without 'type' field are treated like properties with 'type' = 'object'
                children_properties = find_properties_object([], field, properties[field])
                is_nested_array = False
                json_column_name = column_names[field][1]
            elif is_array(properties[field]["type"]) and "items" in properties[field]:
                quoted_field = column_names[field][1]
                children_properties = find_properties_object([], field, properties[field]["items"])
                is_nested_array = True
                json_column_name = f"unnested_column_value({quoted_field})"
            if children_properties:
                for child_key in children_properties:
                    stream_processor = StreamProcessor.create_from_parent(
                        parent=self,
                        child_name=field,
                        json_column_name=json_column_name,
                        properties=children_properties[child_key],
                        is_nested_array=is_nested_array,
                        from_table=from_table,
                    )
                    children.append(stream_processor)
        return children

    def generate_json_parsing_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
{{ unnesting_before_query }}
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    _airbyte_emitted_at
from {{ from_table }}
{{ unnesting_after_query }}
{{ sql_table_comment }}
"""
        )
        sql = template.render(
            unnesting_before_query=self.unnesting_before_query(),
            parent_hash_id=self.parent_hash_id(),
            fields=self.extract_json_columns(column_names),
            from_table=jinja_call(from_table),
            unnesting_after_query=self.unnesting_after_query(),
            sql_table_comment=self.sql_table_comment(),
        )
        return sql

    def extract_json_columns(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [
            StreamProcessor.extract_json_column(field, self.json_column_name, self.properties[field], column_names[field][0])
            for field in column_names
        ]

    @staticmethod
    def extract_json_column(property_name: str, json_column_name: str, definition: Dict, column_name: str) -> str:
        json_path = [property_name]
        json_extract = jinja_call(f"json_extract({json_column_name}, {json_path})")
        if "type" in definition:
            if is_array(definition["type"]):
                json_extract = jinja_call(f"json_extract_array({json_column_name}, {json_path})")
            elif is_object(definition["type"]):
                json_extract = jinja_call(f"json_extract({json_column_name}, {json_path})")
            elif is_simple_property(definition["type"]):
                json_extract = jinja_call(f"json_extract_scalar({json_column_name}, {json_path})")
        return f"{json_extract} as {column_name}"

    def generate_column_typing_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    _airbyte_emitted_at
from {{ from_table }}
{{ sql_table_comment }}
    """
        )
        sql = template.render(
            parent_hash_id=self.parent_hash_id(),
            fields=self.cast_property_types(column_names),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(),
        )
        return sql

    def cast_property_types(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [self.cast_property_type(field, column_names[field][0], column_names[field][1]) for field in column_names]

    def cast_property_type(self, property_name: str, column_name: str, jinja_column: str) -> str:
        definition = self.properties[property_name]
        if "type" not in definition:
            print(f"WARN: Unknown type for column {property_name} at {self.current_json_path()}")
            return column_name
        elif is_array(definition["type"]):
            return self.cast_property_type_as_array(property_name, column_name)
        elif is_object(definition["type"]):
            sql_type = self.cast_property_type_as_object(property_name, column_name)
        # Treat simple types from narrower to wider scope type: boolean < integer < number < string
        elif is_boolean(definition["type"]):
            cast_operation = jinja_call(f"cast_to_boolean({jinja_column})")
            return f"{cast_operation} as {column_name}"
        elif is_integer(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_bigint()")
        elif is_number(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_float()")
        elif is_string(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_string()")
        else:
            print(f"WARN: Unknown type {definition['type']} for column {property_name} at {self.current_json_path()}")
            return column_name
        return f"cast({column_name} as {sql_type}) as {column_name}"

    def cast_property_type_as_array(self, property_name: str, column_name: str) -> str:
        if self.destination_type.value == DestinationType.BIGQUERY.value:
            # TODO build a struct/record type from properties JSON schema
            pass
        return column_name

    def cast_property_type_as_object(self, property_name: str, column_name: str) -> str:
        if self.destination_type.value == DestinationType.BIGQUERY.value:
            # TODO build a struct/record type from properties JSON schema
            pass
        return jinja_call("type_json()")

    def generate_id_hashing_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ '{{' }} dbt_utils.surrogate_key([
      {%- if parent_hash_id %}
        '{{ parent_hash_id }}',
      {%- endif %}
      {%- for field in fields %}
        {{ field }},
      {%- endfor %}
    ]) {{ '}}' }} as {{ hash_id }}
from {{ from_table }}
{{ sql_table_comment }}
    """
        )
        sql = template.render(
            parent_hash_id=self.parent_hash_id(),
            fields=self.safe_cast_to_strings(column_names),
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(),
        )
        return sql

    def safe_cast_to_strings(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [StreamProcessor.safe_cast_to_string(field, self.properties[field], column_names[field][1]) for field in column_names]

    @staticmethod
    def safe_cast_to_string(property_name: str, definition: Dict, column_name: str) -> str:
        if "type" not in definition:
            return column_name
        elif is_boolean(definition["type"]):
            return f"boolean_to_string({column_name})"
        elif is_array(definition["type"]):
            return f"array_to_string({column_name})"
        else:
            return column_name

    def generate_dedup_record_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to prepare for deduplicating records based on the hash record column
select
  *,
  row_number() over (
    partition by {{ hash_id }}
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num
from {{ from_table }}
{{ sql_table_comment }}
        """
        )
        sql = template.render(
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(include_from_table=True),
        )
        return sql

    def generate_scd_type_2_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    {{ cursor_field }} as _airbyte_start_at,
    lag({{ cursor_field }}) over (
        partition by {{ primary_key }}
        order by {{ cursor_field }} desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag({{ cursor_field }}) over (
        partition by {{ primary_key }}
        order by {{ cursor_field }} desc, _airbyte_emitted_at desc
    ) is null as _airbyte_active_row,
    _airbyte_emitted_at,
    {{ hash_id }}
from {{ from_table }}
{{ sql_table_comment }}
        """
        )
        sql = template.render(
            parent_hash_id=self.parent_hash_id(),
            fields=self.list_fields(column_names),
            cursor_field=self.get_cursor_field(column_names),
            primary_key=self.get_primary_key(column_names),
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(include_from_table=True),
        )
        return sql

    def get_cursor_field(self, column_names: Dict[str, Tuple[str, str]]) -> str:
        if self.cursor_field and len(self.cursor_field) == 1:
            return column_names[self.cursor_field[0]][0]
        else:
            if self.cursor_field:
                raise ValueError(f"Unsupported nested cursor field {'.'.join(self.cursor_field)} for stream {self.stream_name}")
            else:
                raise ValueError(f"No cursor field specified for stream {self.stream_name}")

    def get_primary_key(self, column_names: Dict[str, Tuple[str, str]]) -> str:
        if self.primary_key and len(self.primary_key) > 0:
            return ", ".join([self.get_primary_key_from_path(column_names, path) for path in self.primary_key])
        else:
            raise ValueError(f"No primary key specified for stream {self.stream_name}")

    def get_primary_key_from_path(self, column_names: Dict[str, Tuple[str, str]], path: List[str]) -> str:
        if path and len(path) == 1:
            return column_names[path[0]][0]
        else:
            if path:
                raise ValueError(f"Unsupported nested path {'.'.join(path)} for stream {self.stream_name}")
            else:
                raise ValueError(f"No path specified for stream {self.stream_name}")

    def generate_final_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- Final base SQL model
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    _airbyte_emitted_at,
    {{ hash_id }}
from {{ from_table }}
{{ sql_table_comment }}
    """
        )
        sql = template.render(
            parent_hash_id=self.parent_hash_id(),
            fields=self.list_fields(column_names),
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(include_from_table=True),
        )
        return sql

    def list_fields(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [column_names[field][0] for field in column_names]

    def add_to_outputs(self, sql: str, is_intermediate: bool, suffix: str = "") -> str:
        schema = self.get_schema(is_intermediate)
        table_name = self.generate_new_table_name(is_intermediate, suffix)
        self.add_table_to_local_registry(table_name)
        file = f"{table_name}.sql"
        if is_intermediate:
            output = os.path.join("airbyte_views", self.schema, file)
        else:
            output = os.path.join("airbyte_tables", self.schema, file)
        tags = self.get_model_tags(is_intermediate)
        header = jinja_call(f'config(schema="{schema}", tags=[{tags}])')
        self.sql_outputs[
            output
        ] = f"""
{header}
{sql}
"""
        json_path = self.current_json_path()
        print(f"  Generating {output} from {json_path}")
        return ref_table(table_name)

    def get_model_tags(self, is_intermediate: bool) -> str:
        tags = ""
        if self.parent:
            tags += "nested"
        else:
            tags += "top-level"
        if is_intermediate:
            tags += "-intermediate"
        return f'"{tags}"'

    def generate_new_table_name(self, is_intermediate: bool, suffix: str) -> str:
        """
        Generates a new table names that is not registered in the schema yet (based on normalized_stream_name())
        """
        tables_registry = self.tables_registry.union(self.local_registry)
        new_table_name = self.normalized_stream_name()
        if not is_intermediate and self.parent is None:
            if suffix:
                norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
                new_table_name = new_table_name + norm_suffix
            # Top-level stream has priority on table_names
            if new_table_name in tables_registry:
                # TODO handle collisions between different schemas (dbt works with only one schema for ref()?)
                # so filenames should always be different for dbt but the final table can be same as long as schemas are different:
                # see alias in dbt: https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-custom-aliases/
                raise ValueError(f"Conflict: Table name {new_table_name} already exists!")
        elif not self.parent:
            new_table_name = get_table_name(self.name_transformer, "", new_table_name, suffix, self.json_path)
        else:
            new_table_name = get_table_name(self.name_transformer, "_".join(self.json_path[:-1]), new_table_name, suffix, self.json_path)
        new_table_name = self.name_transformer.normalize_table_name(new_table_name, False, False)
        if not is_intermediate:
            self.final_table_name = new_table_name
        return new_table_name

    def add_table_to_local_registry(self, table_name: str):
        tables_registry = self.tables_registry.union(self.local_registry)
        if table_name not in tables_registry:
            self.local_registry.add(table_name)
        else:
            raise KeyError(f"Duplicate table {table_name}")

    def get_schema(self, is_intermediate: bool) -> str:
        if is_intermediate:
            return self.raw_schema
        else:
            return self.schema

    def current_json_path(self) -> str:
        return "/".join(self.json_path)

    def normalized_stream_name(self) -> str:
        """
        This is the normalized name of this stream to be used as a table (different as referring it as a column).
        Note that it might not be the actual table name in case of collisions with other streams (see actual_table_name)...
        """
        return self.name_transformer.normalize_table_name(self.stream_name)

    def actual_table_name(self) -> str:
        """
        Record the final actual name of the table for this stream once it is written.
        (to be used by children stream processors that need to still refer to their actual parent table)
        """
        if self.final_table_name:
            return self.final_table_name
        else:
            raise KeyError("Final table name is not determined yet...")

    def sql_table_comment(self, include_from_table: bool = False) -> str:
        result = f"-- {self.normalized_stream_name()}"
        if len(self.json_path) > 1:
            result += f" at {self.current_json_path()}"
        if include_from_table:
            from_table = jinja_call(self.from_table)
            result += f" from {from_table}"
        return result

    def hash_id(self) -> str:
        return self.name_transformer.normalize_column_name(f"_airbyte_{self.normalized_stream_name()}_hashid")

    # Nested Streams

    def parent_hash_id(self) -> str:
        if self.parent:
            return self.parent.hash_id()
        return ""

    def unnesting_before_query(self) -> str:
        if self.parent and self.is_nested_array:
            parent_table_name = f"'{self.parent.actual_table_name()}'"
            parent_stream_name = f"'{self.parent.normalized_stream_name()}'"
            quoted_field = self.name_transformer.normalize_column_name(self.stream_name, in_jinja=True)
            return jinja_call(f"unnest_cte({parent_table_name}, {parent_stream_name}, {quoted_field})")
        return ""

    def unnesting_after_query(self) -> str:
        result = ""
        if self.parent:
            cross_join = ""
            if self.is_nested_array:
                parent_stream_name = f"'{self.parent.normalized_stream_name()}'"
                quoted_field = self.name_transformer.normalize_column_name(self.stream_name, in_jinja=True)
                cross_join = jinja_call(f"cross_join_unnest({parent_stream_name}, {quoted_field})")
            column_name = self.name_transformer.normalize_column_name(self.stream_name)
            result = f"""
{cross_join}
where {column_name} is not null"""
        return result


# Static Functions


def ref_table(table_name) -> str:
    return f"ref('{table_name}')"


def find_properties_object(path: List[str], field: str, properties) -> Dict[str, Dict]:
    """
    This function is trying to look for a nested "properties" node under the current JSON node to
    identify all nested objects.

    @param path JSON path traversed so far to arrive to this node
    @param field is the current field being considered in the Json Tree
    @param properties is the child tree of properties of the current field being searched
    """
    result = {}
    current_path = path + [field]
    current = "_".join(current_path)
    if isinstance(properties, str) or isinstance(properties, int):
        return {}
    else:
        if "items" in properties:
            return find_properties_object(path, field, properties["items"])
        elif "properties" in properties:
            # we found a properties object
            return {current: properties["properties"]}
        elif "type" in properties and is_simple_property(properties["type"]):
            # we found a basic type
            return {current: {}}
        elif isinstance(properties, dict):
            for key in properties.keys():
                child = find_properties_object(path=current_path, field=key, properties=properties[key])
                if child:
                    result.update(child)
        elif isinstance(properties, list):
            for item in properties:
                child = find_properties_object(path=current_path, field=field, properties=item)
                if child:
                    result.update(child)
    return result


def hash_json_path(json_path: List[str]) -> str:
    lineage = "&airbyte&".join(json_path)
    h = hashlib.sha1()
    h.update(lineage.encode("utf-8"))
    return h.hexdigest()[:3]


def get_table_name(name_transformer: DestinationNameTransformer, parent: str, child: str, suffix: str, json_path: List[str]) -> str:
    max_length = name_transformer.get_name_max_length() - 2  # less two for the underscores
    json_path_hash = hash_json_path(json_path)
    norm_suffix = suffix if not suffix or suffix.startswith("_") else f"_{suffix}"
    norm_parent = parent if not parent else name_transformer.normalize_table_name(parent, False, False)
    norm_child = name_transformer.normalize_table_name(child, False, False)
    min_parent_length = min(MINIMUM_PARENT_LENGTH, len(norm_parent))

    # no parent
    if not parent:
        return name_transformer.truncate_identifier_name(f"{norm_child}{norm_suffix}")
    # if everything fits without truncation, don't truncate anything
    elif (len(norm_parent) + len(norm_child) + len(json_path_hash) + len(norm_suffix)) < max_length:
        return f"{norm_parent}_{json_path_hash}_{norm_child}{norm_suffix}"
    # if everything fits except for the parent, just truncate the parent
    elif (len(norm_child) + len(json_path_hash) + len(norm_suffix)) < (max_length - min_parent_length):
        max_parent_length = max_length - len(norm_child) - len(json_path_hash) - len(norm_suffix)
        return f"{norm_parent[:max_parent_length]}_{json_path_hash}_{norm_child}{norm_suffix}"
    # otherwise first truncate parent to the minimum length and middle truncate the child
    else:
        norm_child_max_length = max_length - min_parent_length - len(json_path_hash) - len(norm_suffix)
        trunc_norm_child = name_transformer.truncate_identifier_name(norm_child, norm_child_max_length)
        return f"{norm_parent[:min_parent_length]}_{json_path_hash}_{trunc_norm_child}{norm_suffix}"
