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

import argparse
import json
import os
import unicodedata as ud
from re import match, sub
from typing import Dict, List, Optional, Set

import yaml
from jinja2 import Template

from .reserved_keywords import is_reserved_keyword


class TransformCatalog:
    """
To run this transformation:
```
python3 main_dev_transform_catalog.py \
  --integration-type <postgres|bigquery|redshift|snowflake>
  --profile-config-dir . \
  --catalog integration_tests/catalog.json \
  --out dir \
  --json-column json_blob
```
    """

    config: dict = {}

    def __init__(self):
        self.config = {}

    def run(self, args) -> None:
        self.parse(args)
        self.process_catalog()

    def parse(self, args) -> None:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--integration-type", type=str, required=True, help="type of integration dialect to use")
        parser.add_argument("--profile-config-dir", type=str, required=True, help="path to directory containing DBT profiles.yml")
        parser.add_argument("--catalog", nargs="+", type=str, required=True, help="path to Catalog (JSON Schema) file")
        parser.add_argument("--out", type=str, required=True, help="path to output generated DBT Models to")
        parser.add_argument("--json-column", type=str, required=False, help="name of the column containing the json blob")
        parsed_args = parser.parse_args(args)
        profiles_yml = read_profiles_yml(parsed_args.profile_config_dir)
        self.config = {
            "integration_type": parsed_args.integration_type,
            "schema": extract_schema(profiles_yml),
            "catalog": parsed_args.catalog,
            "output_path": parsed_args.out,
            "json_column": parsed_args.json_column,
        }

    def process_catalog(self) -> None:
        integration_type = self.config["integration_type"]
        output = self.config["output_path"]
        schema = self.config["schema"]
        for catalog_file in self.config["catalog"]:
            print(f"Processing {catalog_file}...")
            catalog = read_json_catalog(catalog_file)
            print(json.dumps(catalog, separators=(",", ":")))
            sources = generate_dbt_model(
                schema=schema, output=output, integration_type=integration_type, catalog=catalog, json_col=self.config["json_column"]
            )
            write_yaml_sources(output=output, sources=sources, integration_type=integration_type)


def read_profiles_yml(profile_dir: str) -> dict:
    with open(os.path.join(profile_dir, "profiles.yml"), "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        obj = config["normalize"]["outputs"]["prod"]
        return obj


def extract_schema(profiles_yml: dict) -> str:
    if "dataset" in profiles_yml:
        return profiles_yml["dataset"]
    else:
        return profiles_yml["schema"]


def generate_dbt_model(schema: str, output: str, integration_type: str, catalog: dict, json_col: str) -> Dict[str, Set[str]]:
    source_tables: Dict[str, Set[str]] = {}
    all_tables: Dict[str, Set[str]] = {}
    for configuredStream in catalog["streams"]:
        stream = get_field(configuredStream, "stream", "Stream is not defined in Catalog Streams")
        schema = normalize_schema_table_name(schema, integration_type)
        name = get_field(stream, "name", "name is not defined in stream: " + str(stream))
        raw_name = normalize_schema_table_name(f"_airbyte_raw_{name}", integration_type)

        if schema not in source_tables:
            source_tables[schema] = set()
            all_tables[schema] = set()
        if raw_name not in source_tables[schema]:
            source_tables[schema].add(raw_name)
            source_tables[schema].add(name)
            all_tables[schema].add(raw_name)
            all_tables[schema].add(name)
        else:
            raise KeyError(f"Duplicate table {name} in {schema}")
    for configuredStream in catalog["streams"]:
        stream = get_field(configuredStream, "stream", "Stream is not defined in Catalog Streams")

        schema = normalize_schema_table_name(schema, integration_type)
        name = get_field(stream, "name", "name is not defined in stream: " + str(stream))

        raw_schema = normalize_schema_table_name("_airbyte_" + schema, integration_type)
        raw_name = normalize_schema_table_name(f"_airbyte_raw_{name}", integration_type)

        message = f"json_schema is not defined for stream {name}"
        properties = get_field(get_field(stream, "json_schema", message), "properties", message)

        table = jinja_call("source('{}', '{}')".format(schema, raw_name))

        # Check properties
        if not properties:
            raise EOFError("Unexpected empty properties in catalog")

        process_node(
            output=output,
            integration_type=integration_type,
            path=[name],
            json_col=f"'{json_col}'",
            tables_in_schema=all_tables,
            properties=properties,
            raw_schema=raw_schema,
            schema=schema,
            name=name,
            table=table,
            parent_hash_id="",
            inject_sql_prefix="",
            inject_sql_suffix="",
        )
    return source_tables


def get_field(config, key, message):
    if key in config:
        return config[key]
    else:
        raise KeyError(message)


def process_node(
    output: str,
    integration_type: str,
    path: list,
    json_col: str,
    tables_in_schema: Dict[str, Set[str]],
    properties,
    raw_schema,
    schema,
    name,
    table,
    parent_hash_id: str,
    inject_sql_prefix: str,
    inject_sql_suffix: str,
):
    # Check properties
    if not properties:
        print(f"Ignoring '{name}' nested field from {'/'.join(path)} because properties list is empty")
        return

    # Generate JSON Parsing model
    sql_file_name = normalize_schema_table_name("ab1_{}".format(name), integration_type)
    template = Template(
        """
{{ inject_sql_prefix }}
select
{%- if parent_hash_id %}
    {{ parent_hash_id }},
{%- endif %}
{%- for field in fields %}
  {%- if field %}
    {{ field }},
  {%- endif %}
{%- endfor %}
    _airbyte_emitted_at
from {{ table }}
{{ inject_sql_suffix }}
{%- if len(path) > 1 %}
-- {{ name }} from {{ "/".join(path) }}
{%- endif %}
"""
    )
    template.globals["len"] = len
    sql = template.render(
        inject_sql_prefix=inject_sql_prefix,
        parent_hash_id=parent_hash_id,
        fields=[
            json_extract_property(json_col=json_col, name=field, definition=properties[field], integration_type=integration_type)
            for field in properties.keys()
            if not is_airbyte_column(field)
        ],
        table=table,
        inject_sql_suffix=inject_sql_suffix,
        name=normalize_schema_table_name(name, integration_type),
        path=path,
    )
    output_sql_view(output, raw_schema, sql_file_name, sql, path)

    # Generate column typing model
    previous_sql_file_name = sql_file_name
    table = "{{ ref('" + previous_sql_file_name + "') }}"
    sql_file_name = normalize_schema_table_name("ab2_{}".format(name), integration_type)
    sql = template.render(
        inject_sql_prefix="",
        parent_hash_id=parent_hash_id,
        fields=[
            cast_property_type(name=field, definition=properties[field], integration_type=integration_type)
            for field in properties.keys()
            if not is_airbyte_column(field)
        ],
        table=table,
        inject_sql_suffix="",
        name=normalize_schema_table_name(name, integration_type),
        path="/".join(path),
    )
    output_sql_view(output, raw_schema, sql_file_name, sql, path)

    hash_id = quote_column(f"_airbyte_{normalize_schema_table_name(name, integration_type)}_hashid", integration_type)
    # Generate hash_id column model
    previous_sql_file_name = sql_file_name
    table = "{{ ref('" + previous_sql_file_name + "') }}"
    sql_file_name = normalize_schema_table_name("ab3_{}".format(name), integration_type)
    template = Template(
        """
select
    *,
    {{ '{{' }} dbt_utils.surrogate_key([
{%- if parent_hash_id %}
      '{{ parent_hash_id }}',
{%- endif %}
{%- if fields %}
  {%- for field in fields %}
    {%- if field %}
      {{ field }},
    {%- endif %}
  {%- endfor %}
    ]) {{ '}}' }} as {{ hash_id }}
{%- else %}
      null as {{ hash_id }}
{%- endif %}
from {{ table }}
{%- if len(path) > 1 %}
-- {{ name }} from {{ "/".join(path) }}
{%- endif %}
"""
    )
    template.globals["len"] = len
    sql = template.render(
        parent_hash_id=parent_hash_id,
        fields=[
            safe_cast_to_varchar(name=field, definition=properties[field], integration_type=integration_type)
            for field in properties.keys()
            if not is_airbyte_column(field)
        ],
        hash_id=hash_id,
        table=table,
        name=normalize_schema_table_name(name, integration_type),
        path=path,
    )
    output_sql_view(output, raw_schema, sql_file_name, sql, path)

    # Generate final model
    previous_sql_file_name = sql_file_name
    table = "{{ ref('" + previous_sql_file_name + "') }}"
    sql_file_name = normalize_schema_table_name(name, integration_type)
    template = Template(
        """
select
{%- if parent_hash_id %}
    {{ parent_hash_id }},
{%- endif %}
{%- for field in fields %}
  {%- if field %}
    {{ field }},
  {%- endif %}
{%- endfor %}
    _airbyte_emitted_at,
    {{ hash_id }}
from {{ table }}
{%- if len(path) > 1 %}
-- {{ name }} from {{ "/".join(path) }}
{%- endif %}
"""
    )
    template.globals["len"] = len
    sql = template.render(
        parent_hash_id=parent_hash_id,
        fields=[quote_column(field, integration_type) for field in properties.keys() if not is_airbyte_column(field)],
        hash_id=hash_id,
        table=table,
        name=normalize_schema_table_name(name, integration_type),
        path=path,
    )
    output_sql_table(output, schema, sql_file_name, sql, path)

    # Generate children models
    previous_sql_file_name = sql_file_name
    table = "{{ ref('" + previous_sql_file_name + "') }}"
    for field in properties.keys():
        if is_airbyte_column(field):
            pass
        elif is_combining_node(properties[field]):
            # TODO: merge properties of all combinations
            pass
        elif "type" not in properties[field] or is_object(properties[field]["type"]):
            process_nested_property(
                output=output,
                integration_type=integration_type,
                path=path,
                json_col=f"'{field}'",
                tables_in_schema=tables_in_schema,
                properties=properties[field],
                raw_schema=raw_schema,
                schema=schema,
                table=table,
                parent_hash_id=hash_id,
                inject_sql_prefix="",
                inject_sql_suffix=f"where {quote_column(field, integration_type)} is not null\n",
                field=field,
            )
        elif is_array(properties[field]["type"]) and "items" in properties[field]:
            quoted_name = f"'{normalize_schema_table_name(name, integration_type)}'"
            quoted_field = quote_column(field, integration_type, in_jinja=True)
            process_nested_property(
                output=output,
                integration_type=integration_type,
                path=(path),
                json_col="unnested_column_value('_airbyte_data')",
                tables_in_schema=tables_in_schema,
                properties=properties[field]["items"],
                raw_schema=raw_schema,
                schema=schema,
                table=table,
                parent_hash_id=hash_id,
                inject_sql_prefix=jinja_call(f"unnest_cte({quoted_name}, {quoted_field})"),
                inject_sql_suffix="""
{}
where {} is not null
""".format(
                    jinja_call(f"cross_join_unnest({quoted_name}, {quoted_field})"), quote_column(field, integration_type)
                ),
                field=field,
            )


def process_nested_property(
    output: str,
    integration_type: str,
    path: list,
    json_col: str,
    tables_in_schema: Dict[str, Set[str]],
    properties,
    raw_schema,
    schema,
    table,
    parent_hash_id: str,
    inject_sql_prefix: str,
    inject_sql_suffix: str,
    field: str,
):
    children = find_properties_object(path=[], field=field, properties=properties, integration_type=integration_type)
    for child in children:
        child_name = child
        if child_name in tables_in_schema[schema]:
            child_str = normalize_schema_table_name(child_name, integration_type)
            for i in range(1, 100):
                if f"{child_str}_{i}" not in tables_in_schema[schema]:
                    child_name = f"{child_str}_{i}"
                    break
        tables_in_schema[schema].add(child_name)
        process_node(
            output=output,
            integration_type=integration_type,
            path=(path + [child]),
            json_col=json_col,
            tables_in_schema=tables_in_schema,
            properties=children[child],
            raw_schema=raw_schema,
            schema=schema,
            name=child_name,
            table=table,
            parent_hash_id=parent_hash_id,
            inject_sql_prefix=inject_sql_prefix,
            inject_sql_suffix=inject_sql_suffix,
        )


def read_json_catalog(input_path: str) -> dict:
    with open(input_path, "r") as file:
        contents = file.read()
    return json.loads(contents)


def is_string(property_type) -> bool:
    return property_type == "string" or "string" in property_type


def is_integer(property_type) -> bool:
    return property_type == "integer" or "integer" in property_type


def is_number(property_type) -> bool:
    return property_type == "number" or "number" in property_type


def is_boolean(property_type) -> bool:
    return property_type == "boolean" or "boolean" in property_type


def is_array(property_type) -> bool:
    return property_type == "array" or "array" in property_type


def is_object(property_type) -> bool:
    return property_type == "object" or "object" in property_type


def is_airbyte_column(name: str) -> bool:
    return name.startswith("_airbyte_")


def is_simple_property(property_type) -> bool:
    return is_string(property_type) or is_integer(property_type) or is_number(property_type) or is_boolean(property_type)


def is_combining_node(properties: dict) -> set:
    return set(properties).intersection({"anyOf", "oneOf", "allOf"})


def jinja_call(command: str) -> str:
    return "{{ " + command + "  }}"


def strip_accents(s):
    return "".join(c for c in ud.normalize("NFD", s) if ud.category(c) != "Mn")


def normalize_schema_table_name(input_name: str, integration_type: str) -> str:
    # Temporarily disabling the behavior of the ExtendedNameTransformer on table/schema names, see (issue #1785)
    input_name = strip_accents(input_name)
    input_name = sub(r"\s+", "_", input_name)
    input_name = sub(r"[^a-zA-Z0-9_]", "_", input_name)
    input_name = normalize_identifier_name(input_name, integration_type)
    input_name = normalize_identifier_case(input_name, integration_type, is_quoted=False)
    return input_name


def normalize_identifier_name(input_name: str, integration_type: str) -> str:
    if integration_type == "bigquery":
        if len(input_name) >= 1020:
            # bigquery has limit of 1024 characters
            input_name = input_name[0:1020]
        input_name = strip_accents(input_name)
        input_name = sub(r"\s+", "_", input_name)
        doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", input_name[0])
        doesnt_contain_alphanumeric = match(".*[^A-Za-z0-9_].*", input_name)
        if doesnt_start_with_alphaunderscore or doesnt_contain_alphanumeric:
            input_name = f"_{input_name}"
        return sub(r"[^a-zA-Z0-9_]", "_", input_name)
    elif integration_type == "redshift":
        if len(input_name) >= 123:
            # redshift has limit of 127 characters
            input_name = input_name[0:123]
    elif integration_type == "postgres":
        if len(input_name) >= 59:
            # postgres has limit of 63 characters
            input_name = input_name[0:59]
    elif integration_type == "snowflake":
        if len(input_name) >= 251:
            # snowflake has limit of 255 characters
            input_name = input_name[0:251]
    else:
        raise KeyError(f"Unknown integration type {integration_type}")
    return input_name


def normalize_identifier_case(input_name: str, integration_type: str, is_quoted: bool = False):
    if integration_type == "bigquery":
        pass
    elif integration_type == "redshift":
        # all tables (even quoted ones) are coerced to lowercase.
        input_name = input_name.lower()
    elif integration_type == "postgres":
        if input_name[0] != "'" and input_name[0] != '"' and not is_quoted:
            input_name = input_name.lower()
    elif integration_type == "snowflake":
        if input_name[0] != "'" and input_name[0] != '"' and not is_quoted:
            input_name = input_name.upper()
    else:
        raise KeyError(f"Unknown integration type {integration_type}")
    return input_name


def quote_column(input_name: str, integration_type: str, in_jinja=False) -> str:
    if integration_type != "bigquery":
        result = normalize_identifier_name(input_name, integration_type)
        doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", result[0])
        contains_non_alphanumeric = match(".*[^A-Za-z0-9_].*", result)
        if doesnt_start_with_alphaunderscore or contains_non_alphanumeric or is_reserved_keyword(result, integration_type):
            result = f"adapter.quote('{result}')"
            result = normalize_identifier_case(result, integration_type, is_quoted=True)
            if not in_jinja:
                result = jinja_call(result)
            in_jinja = False
        else:
            result = normalize_identifier_case(result, integration_type, is_quoted=False)
    elif is_reserved_keyword(input_name, "bigquery"):
        result = normalize_identifier_name(input_name, "bigquery")
        result = f"adapter.quote('{result}')"
        result = normalize_identifier_case(result, "bigquery", is_quoted=True)
        if not in_jinja:
            result = jinja_call(result)
        in_jinja = False
    else:
        result = normalize_identifier_name(input_name, "bigquery")
        result = normalize_identifier_case(result, "bigquery", is_quoted=False)
    if in_jinja:
        # to refer to columns while already in jinja context, always quote
        return f"'{result}'"
    return result


def find_properties_object(path: List[str], field: str, properties, integration_type: str) -> dict:
    result = {}
    current_path = path + [field]
    current = "_".join(current_path)
    if isinstance(properties, str) or isinstance(properties, int):
        return {}
    else:
        if "items" in properties:
            return find_properties_object(path, field, properties["items"], integration_type=integration_type)
        elif "properties" in properties:
            # we found a properties object
            return {current: properties["properties"]}
        elif "type" in properties and is_simple_property(properties["type"]):
            # we found a basic type
            return {current: None}
        elif isinstance(properties, dict):
            for key in properties.keys():
                child = find_properties_object(path=current_path, field=key, properties=properties[key], integration_type=integration_type)
                if child:
                    result.update(child)
        elif isinstance(properties, list):
            for item in properties:
                child = find_properties_object(path=current_path, field=field, properties=item, integration_type=integration_type)
                if child:
                    result.update(child)
    return result


def json_extract_property(json_col: str, name: str, definition: dict, integration_type: str) -> Optional[str]:
    current = [name]
    if "type" not in definition:
        return "{} as {}".format(jinja_call(f"json_extract({json_col}, {current})"), quote_column(name, integration_type))
    elif is_array(definition["type"]):
        return "{} as {}".format(jinja_call(f"json_extract_array({json_col}, {current})"), quote_column(name, integration_type))
    elif is_object(definition["type"]):
        return "{} as {}".format(jinja_call(f"json_extract({json_col}, {current})"), quote_column(name, integration_type))
    elif is_simple_property(definition["type"]):
        return "{} as {}".format(
            jinja_call(f"json_extract_scalar({json_col}, {current})"),
            quote_column(name, integration_type),
        )
    else:
        return "{} as {}".format(jinja_call(f"json_extract({json_col}, {current})"), quote_column(name, integration_type))


def cast_property_type(name: str, definition: dict, integration_type: str) -> Optional[str]:
    if "type" not in definition:
        print(f"WARN: Unknown type for column {name}")
        return quote_column(name, integration_type)
    elif is_array(definition["type"]):
        # TODO
        return quote_column(name, integration_type)
    elif is_object(definition["type"]):
        # TODO in bq we can build RECORD objects...
        return "cast({} as {}) as {}".format(
            quote_column(name, integration_type),
            jinja_call("type_json()"),
            quote_column(name, integration_type),
        )
    elif is_integer(definition["type"]):
        return "cast({} as {}) as {}".format(
            quote_column(name, integration_type),
            jinja_call("dbt_utils.type_int()"),
            quote_column(name, integration_type),
        )
    elif is_number(definition["type"]):
        return "cast({} as {}) as {}".format(
            quote_column(name, integration_type),
            jinja_call("dbt_utils.type_float()"),
            quote_column(name, integration_type),
        )
    elif is_boolean(definition["type"]):
        return "{} as {}".format(
            jinja_call(f"cast_to_boolean('{name}')"),
            quote_column(name, integration_type),
        )
    elif is_string(definition["type"]):
        return "cast({} as {}) as {}".format(
            quote_column(name, integration_type),
            jinja_call("dbt_utils.type_string()"),
            quote_column(name, integration_type),
        )
    else:
        print(f"WARN: Unknown type {definition['type']} for column {name}")
        return quote_column(name, integration_type)


def safe_cast_to_varchar(name: str, definition: dict, integration_type: str) -> Optional[str]:
    if "type" not in definition:
        return quote_column(name, integration_type, in_jinja=True)
    elif is_boolean(definition["type"]):
        return f"boolean_to_varchar({quote_column(name, integration_type, in_jinja=True)})"
    elif is_array(definition["type"]):
        return f"array_to_varchar({quote_column(name, integration_type, in_jinja=True)})"
    else:
        return quote_column(name, integration_type, in_jinja=True)


def output_sql_view(output: str, schema: str, file: str, sql: str, path: list):
    output = os.path.join(output, "airbyte_views", schema)
    output_sql_file(output, schema, file, sql, path)


def output_sql_table(output: str, schema: str, file: str, sql: str, path: list):
    output = os.path.join(output, "airbyte_tables", schema)
    output_sql_file(output, schema, file, sql, path)


def output_sql_file(output: str, schema: str, file: str, sql: str, path: list):
    if not os.path.exists(output):
        os.makedirs(output)
    header = "{{ config(schema='" + schema + "') }}\n"
    print("  Generating {}.sql from {}:".format(file, "/".join(path)))
    with open(os.path.join(output, f"{file}.sql"), "w") as f:
        f.write(header + sql)


def write_yaml_sources(output: str, sources: Dict[str, Set[str]], integration_type: str) -> None:
    schemas = []
    for schema in sources:
        quoted_schema = schema[0] == '"'
        tables = [
            {
                "name": source,
                "quoting": {"identifier": True},
            }
            for source in sources[schema]
            if normalize_schema_table_name(source, integration_type)[0] == '"'
        ] + [{"name": source} for source in sources[schema] if normalize_schema_table_name(source, integration_type)[0] != '"']
        schemas.append(
            {
                "name": schema,
                "quoting": {
                    "database": True,
                    "schema": quoted_schema,
                    "identifier": False,
                },
                "tables": tables,
            }
        )
    source_config = {"version": 2, "sources": schemas}
    source_path = os.path.join(output, "sources.yml")
    with open(source_path, "w") as fh:
        fh.write(yaml.dump(source_config))


def main(args=None):
    TransformCatalog().run(args)
