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
from typing import List, Optional, Set, Tuple, Union

import yaml


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
        parser.add_argument("--profile-config-dir", type=str, required=True, help="path to directory containing DBT profiles.yml")
        parser.add_argument("--catalog", nargs="+", type=str, required=True, help="path to Catalog (JSON Schema) file")
        parser.add_argument("--out", type=str, required=True, help="path to output generated DBT Models to")
        parser.add_argument("--json-column", type=str, required=False, help="name of the column containing the json blob")
        parsed_args = parser.parse_args(args)
        profiles_yml = read_profiles_yml(parsed_args.profile_config_dir)
        self.config = {
            "schema": extract_schema(profiles_yml),
            "catalog": parsed_args.catalog,
            "output_path": parsed_args.out,
            "json_column": parsed_args.json_column,
        }

    def process_catalog(self) -> None:
        source_tables: set = set()
        schema = self.config["schema"]
        output = self.config["output_path"]
        for catalog_file in self.config["catalog"]:
            print(f"Processing {catalog_file}...")
            catalog = read_json_catalog(catalog_file)
            result, tables = generate_dbt_model(catalog=catalog, json_col=self.config["json_column"], schema=schema)
            self.output_sql_models(output, result)
            source_tables = source_tables.union(tables)
        self.write_yaml_sources(output, schema, source_tables)

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
    def write_yaml_sources(output: str, schema: str, sources: set) -> None:
        tables = [{"name": source} for source in sources]
        source_config = {
            "version": 2,
            "sources": [
                {
                    "name": schema,
                    "tables": tables,
                },
            ],
        }
        # Quoting options are hardcoded and passed down to the sources instead of
        # inheriting them from dbt_project.yml (does not work well for some reasons?)
        # Apparently, Snowflake needs this quoting configuration to work properly...
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


def find_combining_schema(properties: dict) -> set:
    return set(properties).intersection({"anyOf", "oneOf", "allOf"})


def jinja_call(command: str) -> str:
    return "{{ " + command + "  }}"


def json_extract_base_property(path: List[str], json_col: str, name: str, definition: dict) -> Optional[str]:
    current = path + [name]
    if "type" not in definition:
        return None
    elif is_string(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_string()"),
            jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
        )
    elif is_integer(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_int()"),
            jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
        )
    elif is_number(definition["type"]):
        return "cast({} as {}) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call("dbt_utils.type_float()"),
            jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
        )
    elif is_boolean(definition["type"]):
        return "cast({} as boolean) as {}".format(
            jinja_call(f"json_extract_scalar('{json_col}', {current})"),
            jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
        )
    else:
        return None


def json_extract_nested_property(path: List[str], json_col: str, name: str, definition: dict) -> Union[Tuple[None, None], Tuple[str, str]]:
    current = path + [name]
    if definition is None or "type" not in definition:
        return None, None
    elif is_array(definition["type"]):
        return (
            "{} as {}".format(
                jinja_call(f"json_extract_array('{json_col}', {current})"),
                jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
            ),
            "cross join {} as {}".format(
                jinja_call(f"unnest('{name}')"), jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')")
            ),
        )
    elif is_object(definition["type"]):
        return (
            "{} as {}".format(
                jinja_call(f"json_extract('{json_col}', {current})"),
                jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
            ),
            "",
        )
    else:
        return None, None


def select_table(table: str, columns="*"):
    return f"""\nselect {columns} from {jinja_call(f"adapter.quote_as_configured('{table}', 'identifier')")}"""


def extract_node_properties(path: List[str], json_col: str, properties: dict) -> dict:
    result = {}
    if properties:
        for field in properties.keys():
            sql_field = json_extract_base_property(path=path, json_col=json_col, name=field, definition=properties[field])
            if sql_field:
                result[field] = sql_field
    return result


def find_properties_object(path: List[str], field: str, properties) -> dict:
    if isinstance(properties, str) or isinstance(properties, int):
        return {}
    else:
        if "items" in properties:
            return find_properties_object(path, field, properties["items"])
        elif "properties" in properties:
            # we found a properties object
            return {field: properties["properties"]}
        elif "type" in properties and json_extract_base_property(path=path, json_col="", name="", definition=properties):
            # we found a basic type
            return {field: None}
        elif isinstance(properties, dict):
            for key in properties.keys():
                if not json_extract_base_property(path, "", key, properties[key]):
                    child = find_properties_object(path, key, properties[key])
                    if child:
                        return child
        elif isinstance(properties, list):
            for item in properties:
                child = find_properties_object(path=path, field=field, properties=item)
                if child:
                    return child
    return {}


def extract_nested_properties(path: List[str], field: str, properties: dict) -> dict:
    result = {}
    if properties:
        for key in properties.keys():
            combining = find_combining_schema(properties[key])
            if combining:
                # skip combining schemas
                for combo in combining:
                    found = find_properties_object(path=path + [field, key], field=key, properties=properties[key][combo])
                    result.update(found)
            elif "type" not in properties[key]:
                pass
            elif is_array(properties[key]["type"]) and "items" in properties[key]:
                combining = find_combining_schema(properties[key]["items"])
                if combining:
                    # skip combining schemas
                    for combo in combining:
                        found = find_properties_object(path=path + [field, key], field=key, properties=properties[key]["items"][combo])
                        result.update(found)
                else:
                    found = find_properties_object(path=path + [field, key], field=key, properties=properties[key]["items"])
                    result.update(found)
            elif is_object(properties[key]["type"]):
                found = find_properties_object(path=path + [field, key], field=key, properties=properties[key])
                result.update(found)
    return result


def process_node(
    path: List[str], json_col: str, name: str, properties: dict, from_table: str = "", previous="with ", inject_cols=""
) -> dict:
    result = {}
    if previous == "with ":
        prefix = previous
    else:
        prefix = previous + ","
    node_properties = extract_node_properties(path=path, json_col=json_col, properties=properties)
    node_columns = ",\n    ".join([sql for sql in node_properties.values()])
    hash_node_columns = ",\n        ".join([f"adapter.quote_as_configured('{column}', 'identifier')" for column in node_properties.keys()])
    # Disable dbt_utils.surrogate_key for own version to fix a bug with Postgres (#913).
    # hash_node_columns = jinja_call(f"dbt_utils.surrogate_key([\n        {hash_node_columns}\n    ])")
    # We should re-enable it when our PR to dbt_utils is merged
    hash_node_columns = jinja_call(f"surrogate_key([\n        {hash_node_columns}\n    ])")
    hash_id = jinja_call(f"adapter.quote_as_configured('_{name}_hashid', 'identifier')")
    foreign_hash_id = jinja_call(f"adapter.quote_as_configured('_{name}_foreign_hashid', 'identifier')")
    emitted_col = "{},\n    {} as {}".format(
        jinja_call("adapter.quote_as_configured('emitted_at', 'identifier')"),
        jinja_call("dbt_utils.current_timestamp_in_utc()"),
        jinja_call("adapter.quote_as_configured('normalized_at', 'identifier')"),
    )
    node_sql = f"""{prefix}
{jinja_call(f"adapter.quote_as_configured('{name}_node', 'identifier')")} as (
  select {inject_cols}
    {emitted_col},
    {node_columns}
  from {from_table}
),
{jinja_call(f"adapter.quote_as_configured('{name}_with_id', 'identifier')")} as (
  select
    *,
    {hash_node_columns} as {hash_id}
    from {jinja_call(f"adapter.quote_as_configured('{name}_node', 'identifier')")}
)"""
    # SQL Query for current node's basic properties
    result[name] = node_sql + select_table(f"{name}_with_id")

    children_columns = extract_nested_properties(path=path, field=name, properties=properties)
    if children_columns:
        for col in children_columns.keys():
            child_col, join_child_table = json_extract_nested_property(path=path, json_col=json_col, name=col, definition=properties[col])
            column_name = jinja_call(f"adapter.quote_as_configured('{col}', 'identifier')")
            child_sql = f"""{prefix}

{jinja_call(f"adapter.quote_as_configured('{name}_node', 'identifier')")} as (
  select
    {emitted_col},
    {child_col},
    {node_columns}
  from {from_table}
),
{jinja_call(f"adapter.quote_as_configured('{name}_with_id', 'identifier')")} as (
  select
    {hash_node_columns} as {hash_id},
    {column_name}
  from {jinja_call(f"adapter.quote_as_configured('{name}_node', 'identifier')")}
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
                result[f"{name}_{col}"] = child_sql + select_table(
                    f"{name}_with_id",
                    columns=f"""
  {hash_id} as {foreign_hash_id},
  {col}
""",
                )
    return result


def generate_dbt_model(catalog: dict, json_col: str, schema: str) -> Tuple[dict, Set[Union[str]]]:
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
        # TODO Replace {name}_raw by an argument like we do for the json_blob column
        # This would enable destination to freely choose where to store intermediate data before notifying
        # normalization step
        table = jinja_call(f"source('{schema}', '{name}_raw')")
        result.update(process_node(path=[], json_col=json_col, name=name, properties=properties, from_table=table))
        source_tables.add(f"{name}_raw")
    return result, source_tables


def main(args=None):
    TransformCatalog().run(args)
