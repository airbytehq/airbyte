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
from typing import List, Optional, Set, Tuple, Union

import yaml

from .reserved_keywords import is_reserved_keyword


class TransformCatalog:
    """
To run this transformation:
```
python3 main_dev_transform_catalog.py \
  --profile-config-dir . \
  --catalog integration_tests/catalog.json \
  --out dir \
  --json-column json_blob
```
    """

    config: dict = {}

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
        source_tables: set = set()
        integration_type = self.config["integration_type"]
        schema = self.config["schema"]
        output = self.config["output_path"]
        for catalog_file in self.config["catalog"]:
            print(f"Processing {catalog_file}...")
            catalog = read_json_catalog(catalog_file)
            result, tables = generate_dbt_model(
                integration_type=integration_type, catalog=catalog, json_col=self.config["json_column"], schema=schema
            )
            self.output_sql_models(output, result)
            source_tables = source_tables.union(tables)
        self.write_yaml_sources(output, schema, source_tables, integration_type)

    @staticmethod
    def output_sql_models(output: str, result: dict) -> None:
        if result:
            if not os.path.exists(output):
                os.makedirs(output)
            for file, sql in result.items():
                print(f"  Generating {file}.sql in {output}")
                with open(os.path.join(output, f"{file}.sql"), "w") as f:
                    f.write(sql)

    @staticmethod
    def write_yaml_sources(output: str, schema: str, sources: set, integration_type: str) -> None:
        quoted_schema = schema[0] == '"'
        tables = [
            {
                "name": source,
                "quoting": {"identifier": True},
            }
            for source in sources
            if table_name(source, integration_type)[0] == '"'
        ] + [{"name": source} for source in sources if table_name(source, integration_type)[0] != '"']
        source_config = {
            "version": 2,
            "sources": [
                {
                    "name": schema,
                    "quoting": {
                        "database": True,
                        "schema": quoted_schema,
                        "identifier": False,
                    },
                    "tables": tables,
                },
            ],
        }
        source_path = os.path.join(output, "sources.yml")
        if not os.path.exists(source_path):
            with open(source_path, "w") as fh:
                fh.write(yaml.dump(source_config))


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


def find_combining_schema(properties: dict) -> set:
    return set(properties).intersection({"anyOf", "oneOf", "allOf"})


def jinja_call(command: str) -> str:
    return "{{ " + command + "  }}"


def strip_accents(s):
    return "".join(c for c in ud.normalize("NFD", s) if ud.category(c) != "Mn")


# Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785)
def normalize_identifier_name(input_name: str, integration_type: str) -> str:
    if integration_type == "redshift" or integration_type == "postgres":
        input_name = input_name.lower()

    input_name = strip_accents(input_name)
    input_name = sub(r"\s+", "_", input_name)
    return sub(r"[^a-zA-Z0-9_]", "_", input_name)


def table_name(input_name: str, integration_type) -> str:

    if integration_type == "bigquery":
        return normalize_identifier_name(input_name, integration_type)
    elif match("[^A-Za-z_]", input_name[0]) or match(".*[^A-Za-z0-9_].*", input_name):
        return '"' + input_name + '"'
    else:
        if integration_type == "redshift" or integration_type == "postgres":
            return input_name.lower()
        else:
            return input_name


def quote(input_name: str, integration_type: str, in_jinja=False) -> str:
    normalized_input_name = normalize_identifier_name(input_name, integration_type)

    doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", normalized_input_name[0])
    doesnt_contain_alphanumeric = match(".*[^A-Za-z0-9_].*", normalized_input_name)
    if doesnt_start_with_alphaunderscore or doesnt_contain_alphanumeric or is_reserved_keyword(normalized_input_name, integration_type):
        result = f"adapter.quote('{normalized_input_name}')"
    elif in_jinja:
        result = f"'{normalized_input_name}'"
    else:
        return normalized_input_name
    if not in_jinja:
        return jinja_call(result)
    return result


def json_extract_base_property(path: List[str], json_col: str, name: str, definition: dict, integration_type: str) -> Optional[str]:
    current = path + [name]
    if "type" not in definition:
        return None
    elif is_string(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_string()"),
            quote(name, integration_type),
        )
    elif is_integer(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_int()"),
            quote(name, integration_type),
        )
    elif is_number(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_float()"),
            quote(name, integration_type),
        )
    elif is_boolean(definition["type"]):
        # In Redshift, it's not possible to convert from a varchar (which is the output type of json_extract_scalar) to a boolean directly.
        # So we use a macro that handles destination-specific conversions
        return jinja_call(f"cast_to_boolean(json_extract_scalar('{json_col}', {current}))") + f" as {quote(name, integration_type)}"
    else:
        return None


def json_extract_nested_property(
    path: List[str], json_col: str, name: str, definition: dict, integration_type: str
) -> Union[Tuple[None, None], Tuple[str, str]]:
    current = path + [name]
    if definition is None or "type" not in definition:
        return None, None
    elif is_array(definition["type"]):
        return (
            "{} as {}".format(
                jinja_call(f"json_extract_array('{json_col}', {current})"),
                quote(name, integration_type),
            ),
            "cross join {} as {}".format(jinja_call(f"unnest('{name}')"), quote(name, integration_type)),
        )
    elif is_object(definition["type"]):
        return (
            "{} as {}".format(
                jinja_call(f"json_extract('{json_col}', {current})"),
                quote(name, integration_type),
            ),
            "",
        )
    else:
        return None, None


def select_table(table: str, integration_type: str, columns="*"):
    return f"""\nselect {columns} from {table_name(table, integration_type)}"""


def extract_node_properties(path: List[str], json_col: str, properties: dict, integration_type: str) -> dict:
    result = {}
    if properties:
        for field in properties.keys():
            sql_field = json_extract_base_property(
                path=path, json_col=json_col, name=field, definition=properties[field], integration_type=integration_type
            )
            if sql_field and not is_airbyte_column(field):
                result[field] = sql_field
    return result


def find_properties_object(path: List[str], field: str, properties, integration_type: str) -> dict:
    if isinstance(properties, str) or isinstance(properties, int):
        return {}
    else:
        if "items" in properties:
            return find_properties_object(path, field, properties["items"], integration_type=integration_type)
        elif "properties" in properties:
            # we found a properties object
            return {field: properties["properties"]}
        elif "type" in properties and json_extract_base_property(
            path=path, json_col="", name="", definition=properties, integration_type=integration_type
        ):
            # we found a basic type
            return {field: None}
        elif isinstance(properties, dict):
            for key in properties.keys():
                if not json_extract_base_property(path, "", key, properties[key], integration_type=integration_type):
                    child = find_properties_object(path, key, properties[key], integration_type=integration_type)
                    if child:
                        return child
        elif isinstance(properties, list):
            for item in properties:
                child = find_properties_object(path=path, field=field, properties=item, integration_type=integration_type)
                if child:
                    return child
    return {}


def extract_nested_properties(path: List[str], field: str, properties: dict, integration_type: str) -> dict:
    result = {}
    if properties:
        for key in properties.keys():
            combining = find_combining_schema(properties[key])
            if combining:
                # skip combining schemas
                for combo in combining:
                    found = find_properties_object(
                        path=path + [field, key], field=key, properties=properties[key][combo], integration_type=integration_type
                    )
                    result.update(found)
            elif "type" not in properties[key]:
                pass
            elif is_array(properties[key]["type"]) and "items" in properties[key]:
                combining = find_combining_schema(properties[key]["items"])
                if combining:
                    # skip combining schemas
                    for combo in combining:
                        found = find_properties_object(
                            path=path + [field, key],
                            field=key,
                            properties=properties[key]["items"][combo],
                            integration_type=integration_type,
                        )
                        result.update(found)
                else:
                    found = find_properties_object(
                        path=path + [field, key], field=key, properties=properties[key]["items"], integration_type=integration_type
                    )
                    result.update(found)
            elif is_object(properties[key]["type"]):
                found = find_properties_object(
                    path=path + [field, key], field=key, properties=properties[key], integration_type=integration_type
                )
                result.update(found)
    return result


def safe_cast_to_varchar(field: str, integration_type: str, jsonschema_properties: dict):
    # Redshift booleans cannot be directly cast to varchar. So we use a custom macro to convert any boolean columns.
    quoted_field = quote(field, integration_type, in_jinja=True)
    if is_boolean(jsonschema_properties[field]["type"]):
        return f"boolean_to_varchar({quoted_field})"
    else:
        return quoted_field


def process_node(
    path: List[str],
    json_col: str,
    name: str,
    properties: dict,
    integration_type: str,
    from_table: str = "",
    previous="with ",
    inject_cols="",
) -> dict:
    result = {}
    if previous == "with ":
        prefix = previous
    else:
        prefix = previous + ","
    column_to_sql_expression = extract_node_properties(
        path=path, json_col=json_col, properties=properties, integration_type=integration_type
    )

    node_columns = ",\n    ".join([sql for sql in column_to_sql_expression.values()])
    hash_node_columns = ",\n        ".join(
        [safe_cast_to_varchar(column, integration_type, properties) for column in column_to_sql_expression.keys()]
    )
    hash_node_columns = jinja_call(f"dbt_utils.surrogate_key([{hash_node_columns}])")

    hash_id = quote(f"_airbyte_{name}_hashid", integration_type)
    foreign_hash_id = quote(f"_airbyte_{name}_foreign_hashid", integration_type)
    emitted_col = "_airbyte_emitted_at,\n    {} as _airbyte_normalized_at".format(
        jinja_call("dbt_utils.current_timestamp_in_utc()"),
    )
    node_sql = f"""{prefix}
{table_name(f"{name}_node", integration_type)} as (
  select {inject_cols}
    {emitted_col},
    {node_columns}
  from {from_table}
),
{table_name(f"{name}_with_id", integration_type)} as (
  select
    *,
    {hash_node_columns} as {hash_id}
    from {table_name(f"{name}_node", integration_type)}
)"""
    # SQL Query for current node's basic properties
    result[normalize_identifier_name(name, integration_type)] = node_sql + select_table(f"{name}_with_id", integration_type)

    children_columns = extract_nested_properties(path=path, field=name, properties=properties, integration_type=integration_type)
    if children_columns:
        for col in children_columns.keys():
            child_col, join_child_table = json_extract_nested_property(
                path=path, json_col=json_col, name=col, definition=properties[col], integration_type=integration_type
            )
            column_name = quote(col, integration_type)
            child_sql = f"""{prefix}

{table_name(f"{name}_node", integration_type)} as (
  select
    {emitted_col},
    {child_col},
    {node_columns}
  from {from_table}
),
{table_name(f"{name}_with_id", integration_type)} as (
  select
    {hash_node_columns} as {hash_id},
    {column_name}
  from {table_name(f"{name}_node", integration_type)}
  {join_child_table}
)"""
            if children_columns[col]:
                children = process_node(
                    path=[],
                    json_col=col,
                    name=f"{name}_{col}",
                    properties=children_columns[col],
                    from_table=f"{name}_with_id",
                    previous=child_sql,
                    inject_cols=f"\n    {hash_id} as {foreign_hash_id},",
                )
                result.update(children)
            else:
                # SQL Query for current node's basic properties
                result[normalize_identifier_name(f"{name}_{col}", integration_type)] = child_sql + select_table(
                    f"{name}_with_id",
                    integration_type,
                    columns=f"""
  {hash_id} as {foreign_hash_id},
  {col}
""",
                )
    return result


def generate_dbt_model(integration_type: str, catalog: dict, json_col: str, schema: str) -> Tuple[dict, Set[Union[str]]]:
    result = {}
    source_tables = set()
    for configuredStream in catalog["streams"]:
        if "stream" in configuredStream:
            stream = configuredStream["stream"]
        else:
            stream = {}

        if "name" in stream:
            name = stream["name"]
        else:
            name = "undefined"  # todo: should this raise an exception?
        if "json_schema" in stream and "properties" in stream["json_schema"]:
            properties = stream["json_schema"]["properties"]
        else:
            properties = {}
        # TODO Replace '_airbyte_raw_' + name by an argument like we do for the json_blob column
        # This would enable destination to freely choose where to store intermediate data before notifying
        # normalization step
        table = jinja_call(
            f"source('{normalize_identifier_name(schema, integration_type)}', '{normalize_identifier_name('_airbyte_raw_' + name, integration_type)}')"
        )
        result.update(
            process_node(path=[], json_col=json_col, name=name, properties=properties, from_table=table, integration_type=integration_type)
        )
        source_tables.add(normalize_identifier_name("_airbyte_raw_" + name, integration_type))
    return result, source_tables


def main(args=None):
    TransformCatalog().run(args)
