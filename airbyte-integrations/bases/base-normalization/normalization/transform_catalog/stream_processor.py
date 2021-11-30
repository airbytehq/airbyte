#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import os
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple

from airbyte_protocol.models.airbyte_protocol import DestinationSyncMode, SyncMode
from jinja2 import Template
from normalization.destination_type import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer, transform_json_naming
from normalization.transform_catalog.table_name_registry import TableNameRegistry
from normalization.transform_catalog.utils import (
    is_airbyte_column,
    is_array,
    is_boolean,
    is_combining_node,
    is_date,
    is_integer,
    is_number,
    is_object,
    is_simple_property,
    is_string,
    is_timestamp_with_time_zone,
    jinja_call,
    remove_jinja,
)

# using too many columns breaks ephemeral materialization (somewhere between 480 and 490 columns)
# let's use a lower value to be safely away from the limit...
MAXIMUM_COLUMNS_TO_USE_EPHEMERAL = 450


class PartitionScheme(Enum):
    """
    When possible, normalization will try to output partitioned/indexed/sorted tables (depending on the destination support)
    This enum specifies which column to use when doing so (which affects how fast the table can be read using that column as predicate)
    """

    ACTIVE_ROW = "active_row"  # partition by _airbyte_active_row
    UNIQUE_KEY = "unique_key"  # partition by _airbyte_emitted_at, sorted by _airbyte_unique_key
    NOTHING = "nothing"  # no partitions
    DEFAULT = ""  # partition by _airbyte_emitted_at


class TableMaterializationType(Enum):
    """
    Defines the folders and dbt materialization mode of models (as configured in dbt_project.yml file)
    """

    CTE = "airbyte_ctes"
    VIEW = "airbyte_views"
    TABLE = "airbyte_tables"
    INCREMENTAL = "airbyte_incremental"


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
        default_schema: str,
        schema: str,
        source_sync_mode: SyncMode,
        destination_sync_mode: DestinationSyncMode,
        cursor_field: List[str],
        primary_key: List[List[str]],
        json_column_name: str,
        properties: Dict,
        tables_registry: TableNameRegistry,
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
        self.tables_registry: TableNameRegistry = tables_registry
        self.from_table: str = from_table

        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(destination_type)
        self.json_path: List[str] = [stream_name]
        self.final_table_name: str = ""
        self.sql_outputs: Dict[str, str] = {}
        self.parent: Optional["StreamProcessor"] = None
        self.is_nested_array: bool = False
        self.default_schema: str = default_schema
        self.airbyte_ab_id = "_airbyte_ab_id"
        self.airbyte_emitted_at = "_airbyte_emitted_at"
        self.airbyte_normalized_at = "_airbyte_normalized_at"
        self.airbyte_unique_key = "_airbyte_unique_key"

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
        if parent.destination_sync_mode.value == DestinationSyncMode.append_dedup.value:
            # nested streams can't be deduped like their parents (as they may not share the same cursor/primary keys)
            parent_sync_mode = DestinationSyncMode.append
        else:
            parent_sync_mode = parent.destination_sync_mode
        result = StreamProcessor.create(
            stream_name=child_name,
            destination_type=parent.destination_type,
            raw_schema=parent.raw_schema,
            default_schema=parent.default_schema,
            schema=parent.schema,
            source_sync_mode=parent.source_sync_mode,
            destination_sync_mode=parent_sync_mode,
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
        default_schema: str,
        schema: str,
        source_sync_mode: SyncMode,
        destination_sync_mode: DestinationSyncMode,
        cursor_field: List[str],
        primary_key: List[List[str]],
        json_column_name: str,
        properties: Dict,
        tables_registry: TableNameRegistry,
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
            default_schema,
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

    def collect_table_names(self):
        column_names = self.extract_column_names()
        self.tables_registry.register_table(self.get_schema(True), self.get_schema(False), self.stream_name, self.json_path)
        for child in self.find_children_streams(self.from_table, column_names):
            child.collect_table_names()

    def process(self) -> List["StreamProcessor"]:
        """
        See description of StreamProcessor class.
        @return List of StreamProcessor to handle recursively nested columns from this stream
        """
        # Check properties
        if not self.properties:
            print(f"  Ignoring stream '{self.stream_name}' from {self.current_json_path()} because properties list is empty")
            return []

        column_names = self.extract_column_names()
        column_count = len(column_names)

        if column_count == 0:
            print(f"  Ignoring stream '{self.stream_name}' from {self.current_json_path()} because no columns were identified")
            return []

        from_table = self.from_table
        # Transformation Pipeline for this stream
        from_table = self.add_to_outputs(
            self.generate_json_parsing_model(from_table, column_names),
            self.get_model_materialization_mode(is_intermediate=True),
            is_intermediate=True,
            suffix="ab1",
        )
        from_table = self.add_to_outputs(
            self.generate_column_typing_model(from_table, column_names),
            self.get_model_materialization_mode(is_intermediate=True, column_count=column_count),
            is_intermediate=True,
            suffix="ab2",
        )
        if self.destination_sync_mode != DestinationSyncMode.append_dedup:
            from_table = self.add_to_outputs(
                self.generate_id_hashing_model(from_table, column_names),
                self.get_model_materialization_mode(is_intermediate=True, column_count=column_count),
                is_intermediate=True,
                suffix="ab3",
            )
            from_table = self.add_to_outputs(
                self.generate_final_model(from_table, column_names),
                self.get_model_materialization_mode(is_intermediate=False, column_count=column_count),
                is_intermediate=False,
            )
        else:
            if self.is_incremental_mode(self.destination_sync_mode):
                # Force different materialization here because incremental scd models rely on star* macros that requires it
                if DestinationType.POSTGRES.value == self.destination_type.value:
                    # because of https://github.com/dbt-labs/docs.getdbt.com/issues/335, we avoid VIEW for postgres
                    forced_materialization_type = TableMaterializationType.INCREMENTAL
                else:
                    forced_materialization_type = TableMaterializationType.VIEW
            else:
                forced_materialization_type = TableMaterializationType.CTE
            from_table = self.add_to_outputs(
                self.generate_id_hashing_model(from_table, column_names),
                forced_materialization_type,
                is_intermediate=True,
                suffix="stg",
            )
            from_table = self.add_to_outputs(
                self.generate_scd_type_2_model(from_table, column_names),
                self.get_model_materialization_mode(is_intermediate=False, column_count=column_count),
                is_intermediate=False,
                suffix="scd",
                subdir="scd",
                unique_key=self.name_transformer.normalize_column_name("_airbyte_unique_key_scd"),
                partition_by=PartitionScheme.ACTIVE_ROW,
            )
            where_clause = f"\nand {self.name_transformer.normalize_column_name('_airbyte_active_row')} = 1"
            # from_table should not use the de-duplicated final table or tables downstream (nested streams) will miss non active rows
            self.add_to_outputs(
                self.generate_final_model(from_table, column_names, self.get_unique_key()) + where_clause,
                self.get_model_materialization_mode(is_intermediate=False, column_count=column_count),
                is_intermediate=False,
                unique_key=self.get_unique_key(),
                partition_by=PartitionScheme.UNIQUE_KEY,
            )
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
            is_nested_array = False
            json_column_name = ""
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
        if self.destination_type == DestinationType.ORACLE:
            table_alias = ""
        else:
            table_alias = "as table_alias"
        template = Template(
            """
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: {{ from_table }}
{{ unnesting_before_query }}
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    {{ col_ab_id }},
    {{ col_emitted_at }},
    {{ '{{ current_timestamp() }}' }} as {{ col_normalized_at }}
from {{ from_table }} {{ table_alias }}
{{ sql_table_comment }}
{{ unnesting_from }}
where 1 = 1
{{ unnesting_where }}
"""
        )
        sql = template.render(
            col_ab_id=self.get_ab_id(),
            col_emitted_at=self.get_emitted_at(),
            col_normalized_at=self.get_normalized_at(),
            table_alias=table_alias,
            unnesting_before_query=self.unnesting_before_query(),
            parent_hash_id=self.parent_hash_id(),
            fields=self.extract_json_columns(column_names),
            from_table=jinja_call(from_table),
            unnesting_from=self.unnesting_from(),
            unnesting_where=self.unnesting_where(),
            sql_table_comment=self.sql_table_comment(),
        )
        return sql

    def get_ab_id(self, in_jinja: bool = False):
        # this is also tied to dbt-project-template/macros/should_full_refresh.sql
        # as it is needed by the macro should_full_refresh
        return self.name_transformer.normalize_column_name(self.airbyte_ab_id, in_jinja, False)

    def get_emitted_at(self, in_jinja: bool = False):
        return self.name_transformer.normalize_column_name(self.airbyte_emitted_at, in_jinja, False)

    def get_normalized_at(self, in_jinja: bool = False):
        return self.name_transformer.normalize_column_name(self.airbyte_normalized_at, in_jinja, False)

    def get_unique_key(self, in_jinja: bool = False):
        return self.name_transformer.normalize_column_name(self.airbyte_unique_key, in_jinja, False)

    def extract_json_columns(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [
            self.extract_json_column(field, self.json_column_name, self.properties[field], column_names[field][0], "table_alias")
            for field in column_names
        ]

    @staticmethod
    def extract_json_column(property_name: str, json_column_name: str, definition: Dict, column_name: str, table_alias: str) -> str:
        json_path = [property_name]
        # In some cases, some destination aren't able to parse the JSON blob using the original property name
        # we make their life easier by using a pre-populated and sanitized column name instead...
        normalized_json_path = [transform_json_naming(property_name)]
        table_alias = f"{table_alias}"
        if "unnested_column_value" in json_column_name:
            table_alias = ""

        json_extract = jinja_call(f"json_extract('{table_alias}', {json_column_name}, {json_path})")
        if "type" in definition:
            if is_array(definition["type"]):
                json_extract = jinja_call(f"json_extract_array({json_column_name}, {json_path}, {normalized_json_path})")
            elif is_object(definition["type"]):
                json_extract = jinja_call(f"json_extract('{table_alias}', {json_column_name}, {json_path}, {normalized_json_path})")
            elif is_simple_property(definition["type"]):
                json_extract = jinja_call(f"json_extract_scalar({json_column_name}, {json_path}, {normalized_json_path})")

        return f"{json_extract} as {column_name}"

    def generate_column_typing_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        template = Template(
            """
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ from_table }}
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    {{ col_ab_id }},
    {{ col_emitted_at }},
    {{ '{{ current_timestamp() }}' }} as {{ col_normalized_at }}
from {{ from_table }}
{{ sql_table_comment }}
where 1 = 1
    """
        )
        sql = template.render(
            col_ab_id=self.get_ab_id(),
            col_emitted_at=self.get_emitted_at(),
            col_normalized_at=self.get_normalized_at(),
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
            return column_name
        elif is_object(definition["type"]):
            sql_type = jinja_call("type_json()")
        # Treat simple types from narrower to wider scope type: boolean < integer < number < string
        elif is_boolean(definition["type"]):
            cast_operation = jinja_call(f"cast_to_boolean({jinja_column})")
            return f"{cast_operation} as {column_name}"
        elif is_integer(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_bigint()")
        elif is_number(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_float()")
        elif is_timestamp_with_time_zone(definition):
            if self.destination_type == DestinationType.SNOWFLAKE:
                # snowflake uses case when statement to parse timestamp field
                # in this case [cast] operator is not needed as data already converted to timestamp type
                return self.generate_snowflake_timestamp_statement(column_name)
            replace_operation = jinja_call(f"empty_string_to_null({jinja_column})")
            if self.destination_type == DestinationType.MSSQL:
                # in case of datetime, we don't need to use [cast] function, use try_parse instead.
                sql_type = jinja_call("type_timestamp_with_timezone()")
                return f"try_parse({replace_operation} as {sql_type}) as {column_name}"
            # in all other cases
            sql_type = jinja_call("type_timestamp_with_timezone()")
            return f"cast({replace_operation} as {sql_type}) as {column_name}"
        elif is_date(definition):
            if self.destination_type == DestinationType.MYSQL:
                # MySQL does not support [cast] and [nullif] functions together
                return self.generate_mysql_date_format_statement(column_name)
            replace_operation = jinja_call(f"empty_string_to_null({jinja_column})")
            if self.destination_type == DestinationType.MSSQL:
                # in case of date, we don't need to use [cast] function, use try_parse instead.
                sql_type = jinja_call("type_date()")
                return f"try_parse({replace_operation} as {sql_type}) as {column_name}"
            # in all other cases
            sql_type = jinja_call("type_date()")
            return f"cast({replace_operation} as {sql_type}) as {column_name}"
        elif is_string(definition["type"]):
            sql_type = jinja_call("dbt_utils.type_string()")
        else:
            print(f"WARN: Unknown type {definition['type']} for column {property_name} at {self.current_json_path()}")
            return column_name

        return f"cast({column_name} as {sql_type}) as {column_name}"

    @staticmethod
    def generate_mysql_date_format_statement(column_name: str) -> str:
        template = Template(
            """
        case when {{column_name}} = '' then NULL
        else cast({{column_name}} as date)
        end as {{column_name}}
        """
        )
        return template.render(column_name=column_name)

    @staticmethod
    def generate_snowflake_timestamp_statement(column_name: str) -> str:
        """
        Generates snowflake DB specific timestamp case when statement
        """
        formats = [
            {"regex": r"\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}", "format": "YYYY-MM-DDTHH24:MI:SSTZHTZM"},
            {"regex": r"\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}", "format": "YYYY-MM-DDTHH24:MI:SSTZH"},
            {
                "regex": r"\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}",
                "format": "YYYY-MM-DDTHH24:MI:SS.FFTZHTZM",
            },
            {"regex": r"\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}", "format": "YYYY-MM-DDTHH24:MI:SS.FFTZH"},
        ]
        template = Template(
            """
    case
    {% for format_item in formats %}
        when {{column_name}} regexp '{{format_item['regex']}}' then to_timestamp_tz({{column_name}}, '{{format_item['format']}}')
    {% endfor %}
        when {{column_name}} = '' then NULL
    else to_timestamp_tz({{column_name}})
    end as {{column_name}}
    """
        )
        return template.render(formats=formats, column_name=column_name)

    def generate_id_hashing_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:

        template = Template(
            """
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ from_table }}
select
    {{ '{{' }} dbt_utils.surrogate_key([
      {%- if parent_hash_id %}
        {{ parent_hash_id }},
      {%- endif %}
      {%- for field in fields %}
        {{ field }},
      {%- endfor %}
    ]) {{ '}}' }} as {{ hash_id }},
    tmp.*
from {{ from_table }} tmp
{{ sql_table_comment }}
where 1 = 1
    """
        )

        sql = template.render(
            parent_hash_id=self.parent_hash_id(in_jinja=True),
            fields=self.safe_cast_to_strings(column_names),
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(),
        )
        return sql

    def safe_cast_to_strings(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:

        return [
            StreamProcessor.safe_cast_to_string(self.properties[field], column_names[field][1], self.destination_type)
            for field in column_names
        ]

    @staticmethod
    def safe_cast_to_string(definition: Dict, column_name: str, destination_type: DestinationType) -> str:
        """
        Note that the result from this static method should always be used within a
        jinja context (for example, from jinja macro surrogate_key call)

        The jinja_remove function is necessary because of Oracle database, some columns
        are created with {{ quote('column_name') }} and reused the same fields for this
        operation. Because the quote is injected inside a jinja macro we need to remove
        the curly brackets.
        """

        if "type" not in definition:
            col = column_name
        elif is_boolean(definition["type"]):
            col = f"boolean_to_string({column_name})"
        elif is_array(definition["type"]):
            col = f"array_to_string({column_name})"
        else:
            col = column_name

        if destination_type == DestinationType.ORACLE:
            quote_in_parenthesis = re.compile(r"quote\((.*)\)")
            return remove_jinja(col) if quote_in_parenthesis.findall(col) else col

        return col

    def generate_scd_type_2_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]]) -> str:
        scd_sql_template = """
-- depends_on: {{ from_table }}
with
{{ '{% if is_incremental() %}' }}
new_data as (
    -- retrieve incremental "new" data
    select
        *
    from {{'{{'}} {{ from_table }}  {{'}}'}}
    {{ sql_table_comment }}
    where 1 = 1
    {{'{{'}} incremental_clause({{ quoted_col_emitted_at }}) {{'}}'}}
),
new_data_ids as (
    -- build a subset of {{ unique_key }} from rows that are new
    select distinct
        {{ '{{' }} dbt_utils.surrogate_key([
          {%- for primary_key in primary_keys %}
            {{ primary_key }},
          {%- endfor %}
        ]) {{ '}}' }} as {{ unique_key }}
    from new_data
),
empty_new_data as (
    -- build an empty table to only keep the table's column types
    select * from new_data where 1 = 0
),
previous_active_scd_data as (
    -- retrieve "incomplete old" data that needs to be updated with an end date because of new changes
    select
        {{ '{{' }} star_intersect({{ from_table }}, this, from_alias='inc_data', intersect_alias='this_data') {{ '}}' }}
    from {{ '{{ this }}' }} as this_data
    -- make a join with new_data using primary key to filter active data that need to be updated only
    join new_data_ids on this_data.{{ unique_key }} = new_data_ids.{{ unique_key }}
    -- force left join to NULL values (we just need to transfer column types only for the star_intersect macro on schema changes)
    left join empty_new_data as inc_data on this_data.{{ col_ab_id }} = inc_data.{{ col_ab_id }}
    where {{ active_row }} = 1
),
input_data as (
    select {{ '{{' }} dbt_utils.star({{ from_table }}) {{ '}}' }} from new_data
    union all
    select {{ '{{' }} dbt_utils.star({{ from_table }}) {{ '}}' }} from previous_active_scd_data
),
{{ '{% else %}' }}
input_data as (
    select *
    from {{'{{'}} {{ from_table }}  {{'}}'}}
    {{ sql_table_comment }}
),
{{ '{% endif %}' }}
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      {%- if parent_hash_id %}
        {{ parent_hash_id }},
      {%- endif %}
      {{ '{{' }} dbt_utils.surrogate_key([
          {%- for primary_key in primary_keys %}
            {{ primary_key }},
          {%- endfor %}
      ]) {{ '}}' }} as {{ unique_key }},
      {%- for field in fields %}
        {{ field }},
      {%- endfor %}
      {{ cursor_field }} as {{ airbyte_start_at }},
      lag({{ cursor_field }}) over (
        partition by {{ primary_key_partition | join(", ") }}
        order by
            {{ cursor_field }} {{ order_null }},
            {{ cursor_field }} desc,
            {{ col_emitted_at }} desc{{ cdc_updated_at_order }}
      ) as {{ airbyte_end_at }},
      case when row_number() over (
        partition by {{ primary_key_partition | join(", ") }}
        order by
            {{ cursor_field }} {{ order_null }},
            {{ cursor_field }} desc,
            {{ col_emitted_at }} desc{{ cdc_updated_at_order }}
      ) = 1{{ cdc_active_row }} then 1 else 0 end as {{ active_row }},
      {{ col_ab_id }},
      {{ col_emitted_at }},
      {{ hash_id }}
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by {{ unique_key }}, {{ airbyte_start_at }}, {{ col_emitted_at }}{{ cdc_cols }}
            order by {{ col_ab_id }}
        ) as {{ airbyte_row_num }},
        {{ '{{' }} dbt_utils.surrogate_key([
          {{ quoted_unique_key }},
          {{ quoted_airbyte_start_at }},
          {{ quoted_col_emitted_at }}{{ quoted_cdc_cols }}
        ]) {{ '}}' }} as {{ airbyte_unique_key_scd }},
        scd_data.*
    from scd_data
)
select
    {%- if parent_hash_id %}
        {{ parent_hash_id }},
    {%- endif %}
    {{ unique_key }},
    {{ airbyte_unique_key_scd }},
    {%- for field in fields %}
        {{ field }},
    {%- endfor %}
    {{ airbyte_start_at }},
    {{ airbyte_end_at }},
    {{ active_row }},
    {{ col_ab_id }},
    {{ col_emitted_at }},
    {{ '{{ current_timestamp() }}' }} as {{ col_normalized_at }},
    {{ hash_id }}
from dedup_data where {{ airbyte_row_num }} = 1
        """
        template = Template(scd_sql_template)

        order_null = "is null asc"
        if self.destination_type == DestinationType.ORACLE:
            order_null = "asc nulls last"
        if self.destination_type == DestinationType.MSSQL:
            # SQL Server treats NULL values as the lowest values, then sorted in ascending order, NULLs come first.
            order_null = "desc"

        # TODO move all cdc columns out of scd models
        cdc_active_row_pattern = ""
        cdc_updated_order_pattern = ""
        cdc_cols = ""
        quoted_cdc_cols = ""
        if "_ab_cdc_deleted_at" in column_names.keys():
            col_cdc_deleted_at = self.name_transformer.normalize_column_name("_ab_cdc_deleted_at")
            col_cdc_updated_at = self.name_transformer.normalize_column_name("_ab_cdc_updated_at")
            quoted_col_cdc_deleted_at = self.name_transformer.normalize_column_name("_ab_cdc_deleted_at", in_jinja=True)
            quoted_col_cdc_updated_at = self.name_transformer.normalize_column_name("_ab_cdc_updated_at", in_jinja=True)
            cdc_active_row_pattern = f" and {col_cdc_deleted_at} is null"
            cdc_updated_order_pattern = f", {col_cdc_updated_at} desc"
            cdc_cols = (
                f", cast({col_cdc_deleted_at} as "
                + "{{ dbt_utils.type_string() }})"
                + f", cast({col_cdc_updated_at} as "
                + "{{ dbt_utils.type_string() }})"
            )
            quoted_cdc_cols = f", {quoted_col_cdc_deleted_at}, {quoted_col_cdc_updated_at}"

        if "_ab_cdc_log_pos" in column_names.keys():
            col_cdc_log_pos = self.name_transformer.normalize_column_name("_ab_cdc_log_pos")
            quoted_col_cdc_log_pos = self.name_transformer.normalize_column_name("_ab_cdc_log_pos", in_jinja=True)
            cdc_updated_order_pattern += f", {col_cdc_log_pos} desc"
            cdc_cols += f", cast({col_cdc_log_pos} as " + "{{ dbt_utils.type_string() }})"
            quoted_cdc_cols += f", {quoted_col_cdc_log_pos}"

        sql = template.render(
            order_null=order_null,
            airbyte_start_at=self.name_transformer.normalize_column_name("_airbyte_start_at"),
            quoted_airbyte_start_at=self.name_transformer.normalize_column_name("_airbyte_start_at", in_jinja=True),
            airbyte_end_at=self.name_transformer.normalize_column_name("_airbyte_end_at"),
            active_row=self.name_transformer.normalize_column_name("_airbyte_active_row"),
            airbyte_row_num=self.name_transformer.normalize_column_name("_airbyte_row_num"),
            quoted_airbyte_row_num=self.name_transformer.normalize_column_name("_airbyte_row_num", in_jinja=True),
            airbyte_unique_key_scd=self.name_transformer.normalize_column_name("_airbyte_unique_key_scd"),
            unique_key=self.get_unique_key(),
            quoted_unique_key=self.get_unique_key(in_jinja=True),
            col_ab_id=self.get_ab_id(),
            col_emitted_at=self.get_emitted_at(),
            quoted_col_emitted_at=self.get_emitted_at(in_jinja=True),
            col_normalized_at=self.get_normalized_at(),
            parent_hash_id=self.parent_hash_id(),
            fields=self.list_fields(column_names),
            cursor_field=self.get_cursor_field(column_names),
            primary_keys=self.list_primary_keys(column_names),
            primary_key_partition=self.get_primary_key_partition(column_names),
            hash_id=self.hash_id(),
            from_table=from_table,
            sql_table_comment=self.sql_table_comment(include_from_table=True),
            cdc_active_row=cdc_active_row_pattern,
            cdc_updated_at_order=cdc_updated_order_pattern,
            cdc_cols=cdc_cols,
            quoted_cdc_cols=quoted_cdc_cols,
        )
        return sql

    def get_cursor_field(self, column_names: Dict[str, Tuple[str, str]], in_jinja: bool = False) -> str:
        if not self.cursor_field:
            cursor = self.name_transformer.normalize_column_name("_airbyte_emitted_at", in_jinja)
        elif len(self.cursor_field) == 1:
            if not is_airbyte_column(self.cursor_field[0]):
                cursor = column_names[self.cursor_field[0]][0]
            else:
                # using an airbyte generated column
                cursor = self.cursor_field[0]
        else:
            raise ValueError(f"Unsupported nested cursor field {'.'.join(self.cursor_field)} for stream {self.stream_name}")

        return cursor

    def list_primary_keys(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        primary_keys = []
        for key_path in self.primary_key:
            if len(key_path) == 1:
                primary_keys.append(column_names[key_path[0]][1])
            else:
                raise ValueError(f"Unsupported nested path {'.'.join(key_path)} for stream {self.stream_name}")
        return primary_keys

    def get_primary_key_partition(self, column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        if self.primary_key and len(self.primary_key) > 0:
            return [self.get_primary_key_from_path(column_names, path) for path in self.primary_key]
        else:
            raise ValueError(f"No primary key specified for stream {self.stream_name}")

    def get_primary_key_from_path(self, column_names: Dict[str, Tuple[str, str]], path: List[str]) -> str:
        if path and len(path) == 1:
            field = path[0]
            if not is_airbyte_column(field):
                if "type" in self.properties[field]:
                    property_type = self.properties[field]["type"]
                else:
                    property_type = "object"
                if is_number(property_type) or is_object(property_type):
                    # some destinations don't handle float columns (or complex types) as primary keys, turn them to string
                    return f"cast({column_names[field][0]} as {jinja_call('dbt_utils.type_string()')})"
                else:
                    return column_names[field][0]
            else:
                # using an airbyte generated column
                return f"cast({field} as {jinja_call('dbt_utils.type_string()')})"
        else:
            if path:
                raise ValueError(f"Unsupported nested path {'.'.join(path)} for stream {self.stream_name}")
            else:
                raise ValueError(f"No path specified for stream {self.stream_name}")

    def generate_final_model(self, from_table: str, column_names: Dict[str, Tuple[str, str]], unique_key: str = "") -> str:
        template = Template(
            """
-- Final base SQL model
-- depends_on: {{ from_table }}
select
  {%- if parent_hash_id %}
    {{ parent_hash_id }},
  {%- endif %}
  {%- if unique_key %}
    {{ unique_key }},
  {%- endif %}
  {%- for field in fields %}
    {{ field }},
  {%- endfor %}
    {{ col_ab_id }},
    {{ col_emitted_at }},
    {{ '{{ current_timestamp() }}' }} as {{ col_normalized_at }},
    {{ hash_id }}
from {{ from_table }}
{{ sql_table_comment }}
where 1 = 1
    """
        )
        sql = template.render(
            col_ab_id=self.get_ab_id(),
            col_emitted_at=self.get_emitted_at(),
            col_normalized_at=self.get_normalized_at(),
            parent_hash_id=self.parent_hash_id(),
            fields=self.list_fields(column_names),
            hash_id=self.hash_id(),
            from_table=jinja_call(from_table),
            sql_table_comment=self.sql_table_comment(include_from_table=True),
            unique_key=unique_key,
        )
        return sql

    @staticmethod
    def is_incremental_mode(destination_sync_mode: DestinationSyncMode) -> bool:
        return destination_sync_mode.value in [DestinationSyncMode.append.value, DestinationSyncMode.append_dedup.value]

    def add_incremental_clause(self, sql_query: str) -> str:
        template = Template(
            """
{{ sql_query }}
{{'{{'}} incremental_clause({{ col_emitted_at }}) {{'}}'}}
    """
        )
        sql = template.render(
            sql_query=sql_query,
            col_emitted_at=self.get_emitted_at(in_jinja=True),
        )
        return sql

    @staticmethod
    def list_fields(column_names: Dict[str, Tuple[str, str]]) -> List[str]:
        return [column_names[field][0] for field in column_names]

    def add_to_outputs(
        self,
        sql: str,
        materialization_mode: TableMaterializationType,
        is_intermediate: bool = True,
        suffix: str = "",
        unique_key: str = "",
        subdir: str = "",
        partition_by: PartitionScheme = PartitionScheme.DEFAULT,
    ) -> str:
        schema = self.get_schema(is_intermediate)
        # MySQL table names need to be manually truncated, because it does not do it automatically
        truncate_name = self.destination_type == DestinationType.MYSQL
        table_name = self.tables_registry.get_table_name(schema, self.json_path, self.stream_name, suffix, truncate_name)
        file_name = self.tables_registry.get_file_name(schema, self.json_path, self.stream_name, suffix, truncate_name)
        file = f"{file_name}.sql"
        output = os.path.join(materialization_mode.value, subdir, self.schema, file)
        config = self.get_model_partition_config(partition_by, unique_key)
        if file_name != table_name:
            # The alias() macro configs a model's final table name.
            config["alias"] = f'"{table_name}"'
        if self.destination_type == DestinationType.ORACLE:
            # oracle does not allow changing schemas
            config["schema"] = f'"{self.default_schema}"'
        else:
            config["schema"] = f'"{schema}"'
        if self.is_incremental_mode(self.destination_sync_mode):
            if suffix == "scd":
                if self.destination_type != DestinationType.POSTGRES:
                    stg_schema = self.get_schema(True)
                    stg_table = self.tables_registry.get_file_name(schema, self.json_path, self.stream_name, "stg", truncate_name)
                    config["post_hook"] = f"['drop view {stg_schema}.{stg_table}']"
            else:
                # incremental is handled in the SCD SQL already
                sql = self.add_incremental_clause(sql)
        template = Template(
            """
{{ '{{' }} config(
{%- for key in config %}
    {{ key }} = {{ config[key] }},
{%- endfor %}
    tags = [ {{ tags }} ]
) {{ '}}' }}
{{ sql }}
    """
        )
        self.sql_outputs[output] = template.render(config=config, sql=sql, tags=self.get_model_tags(is_intermediate))
        json_path = self.current_json_path()
        print(f"  Generating {output} from {json_path}")
        return ref_table(file_name)

    def get_model_materialization_mode(self, is_intermediate: bool, column_count: int = 0) -> TableMaterializationType:
        if is_intermediate:
            if column_count <= MAXIMUM_COLUMNS_TO_USE_EPHEMERAL:
                return TableMaterializationType.CTE
            else:
                # dbt throws "maximum recursion depth exceeded" exception at runtime
                # if ephemeral is used with large number of columns, use views instead
                return TableMaterializationType.VIEW
        else:
            if self.is_incremental_mode(self.destination_sync_mode):
                return TableMaterializationType.INCREMENTAL
            else:
                return TableMaterializationType.TABLE

    def get_model_partition_config(self, partition_by: PartitionScheme, unique_key: str) -> Dict:
        """
        Defines partition, clustering and unique key parameters for each destination.
        The goal of these are to make read more performant.

        In general, we need to do lookups on the last emitted_at column to know if a record is freshly produced and need to be
        incrementally processed or not.
        But in certain models, such as SCD tables for example, we also need to retrieve older data to update their type 2 SCD end_dates,
        thus a different partitioning scheme is used to optimize that use case.
        """
        config = {}
        if self.destination_type == DestinationType.BIGQUERY:
            # see https://docs.getdbt.com/reference/resource-configs/bigquery-configs
            if partition_by == PartitionScheme.UNIQUE_KEY:
                config["cluster_by"] = '["_airbyte_unique_key","_airbyte_emitted_at"]'
            elif partition_by == PartitionScheme.ACTIVE_ROW:
                config["cluster_by"] = '["_airbyte_unique_key_scd","_airbyte_emitted_at"]'
            else:
                config["cluster_by"] = '"_airbyte_emitted_at"'
            if partition_by == PartitionScheme.ACTIVE_ROW:
                config["partition_by"] = (
                    '{"field": "_airbyte_active_row", "data_type": "int64", ' '"range": {"start": 0, "end": 1, "interval": 1}}'
                )
            elif partition_by == PartitionScheme.NOTHING:
                pass
            else:
                config["partition_by"] = '{"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"}'
        elif self.destination_type == DestinationType.POSTGRES:
            # see https://docs.getdbt.com/reference/resource-configs/postgres-configs
            if partition_by == PartitionScheme.ACTIVE_ROW:
                config["indexes"] = "[{'columns':['_airbyte_active_row','_airbyte_unique_key_scd','_airbyte_emitted_at'],'type': 'btree'}]"
            elif partition_by == PartitionScheme.UNIQUE_KEY:
                config["indexes"] = "[{'columns':['_airbyte_unique_key'],'unique':True}]"
            else:
                config["indexes"] = "[{'columns':['_airbyte_emitted_at'],'type':'hash'}]"
        elif self.destination_type == DestinationType.REDSHIFT:
            # see https://docs.getdbt.com/reference/resource-configs/redshift-configs
            if partition_by == PartitionScheme.ACTIVE_ROW:
                config["sort"] = '["_airbyte_active_row", "_airbyte_unique_key_scd", "_airbyte_emitted_at"]'
            elif partition_by == PartitionScheme.UNIQUE_KEY:
                config["sort"] = '["_airbyte_unique_key", "_airbyte_emitted_at"]'
            elif partition_by == PartitionScheme.NOTHING:
                pass
            else:
                config["sort"] = '"_airbyte_emitted_at"'
        elif self.destination_type == DestinationType.SNOWFLAKE:
            # see https://docs.getdbt.com/reference/resource-configs/snowflake-configs
            if partition_by == PartitionScheme.ACTIVE_ROW:
                config["cluster_by"] = '["_AIRBYTE_ACTIVE_ROW", "_AIRBYTE_UNIQUE_KEY_SCD", "_AIRBYTE_EMITTED_AT"]'
            elif partition_by == PartitionScheme.UNIQUE_KEY:
                config["cluster_by"] = '["_AIRBYTE_UNIQUE_KEY", "_AIRBYTE_EMITTED_AT"]'
            elif partition_by == PartitionScheme.NOTHING:
                pass
            else:
                config["cluster_by"] = '["_AIRBYTE_EMITTED_AT"]'
        if unique_key:
            config["unique_key"] = f'"{unique_key}"'
        elif not self.is_nested_array:
            # in nested arrays, each element is sharing the same _airbyte_ab_id, so it's not unique
            config["unique_key"] = self.get_ab_id(in_jinja=True)
        return config

    def get_model_tags(self, is_intermediate: bool) -> str:
        tags = ""
        if self.parent:
            tags += "nested"
        else:
            tags += "top-level"
        if is_intermediate:
            tags += "-intermediate"
        return f'"{tags}"'

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

    def sql_table_comment(self, include_from_table: bool = False) -> str:
        result = f"-- {self.normalized_stream_name()}"
        if len(self.json_path) > 1:
            result += f" at {self.current_json_path()}"
        if include_from_table:
            from_table = jinja_call(self.from_table)
            result += f" from {from_table}"
        return result

    def hash_id(self, in_jinja: bool = False) -> str:
        hash_id_col = f"_airbyte_{self.normalized_stream_name()}_hashid"
        if self.parent:
            if self.normalized_stream_name().lower() == self.parent.stream_name.lower():
                level = len(self.json_path)
                hash_id_col = f"_airbyte_{self.normalized_stream_name()}_{level}_hashid"

        return self.name_transformer.normalize_column_name(hash_id_col, in_jinja)

    # Nested Streams

    def parent_hash_id(self, in_jinja: bool = False) -> str:
        if self.parent:
            return self.parent.hash_id(in_jinja)
        return ""

    def unnesting_before_query(self) -> str:
        if self.parent and self.is_nested_array:
            parent_file_name = (
                f"'{self.tables_registry.get_file_name(self.parent.get_schema(False), self.parent.json_path, self.parent.stream_name, '')}'"
            )
            parent_stream_name = f"'{self.parent.normalized_stream_name()}'"
            quoted_field = self.name_transformer.normalize_column_name(self.stream_name, in_jinja=True)
            return jinja_call(f"unnest_cte({parent_file_name}, {parent_stream_name}, {quoted_field})")
        return ""

    def unnesting_from(self) -> str:
        if self.parent:
            if self.is_nested_array:
                parent_stream_name = f"'{self.parent.normalized_stream_name()}'"
                quoted_field = self.name_transformer.normalize_column_name(self.stream_name, in_jinja=True)
                return jinja_call(f"cross_join_unnest({parent_stream_name}, {quoted_field})")
        return ""

    def unnesting_where(self) -> str:
        if self.parent:
            column_name = self.name_transformer.normalize_column_name(self.stream_name)
            return f"and {column_name} is not null"
        return ""


# Static Functions


def ref_table(file_name: str) -> str:
    return f"ref('{file_name}')"


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
