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

from typing import List, Optional, Tuple, Union

from normalization.transform_catalog.helper import jinja_call


class JsonSchemaNormalizer:
    catalog: dict = {}

    def __init__(self, catalog: dict):
        self.catalog = catalog

    def generate_dbt_model(self, schema: str, json_col: str, table_suffix: str) -> dict:
        result = {}
        for obj in self.catalog["streams"]:
            if "name" in obj:
                name = obj["name"]
            else:
                name = "undefined"
            if "json_schema" in obj and "properties" in obj["json_schema"]:
                properties = obj["json_schema"]["properties"]
            else:
                properties = {}
            table = jinja_call(f"ref('{name}{table_suffix}')")
            result.update(
                process_node(
                    path=[],
                    json_col=json_col,
                    name=name,
                    properties=properties,
                    from_table=table,
                )
            )
        return result


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
                jinja_call(f"unnest('{name}')"),
                jinja_call(f"adapter.quote_as_configured('{name}', 'identifier')"),
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
                    found = find_properties_object(
                        path=path + [field, key],
                        field=key,
                        properties=properties[key][combo],
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
                        )
                        result.update(found)
                else:
                    found = find_properties_object(
                        path=path + [field, key],
                        field=key,
                        properties=properties[key]["items"],
                    )
                    result.update(found)
            elif is_object(properties[key]["type"]):
                found = find_properties_object(path=path + [field, key], field=key, properties=properties[key])
                result.update(found)
    return result


def process_node(
    path: List[str],
    json_col: str,
    name: str,
    properties: dict,
    from_table: str = "",
    previous="with ",
    inject_cols="",
) -> dict:
    result = {}
    if previous == "with ":
        prefix = previous
    else:
        prefix = previous + ","
    node_properties = extract_node_properties(path=path, json_col=json_col, properties=properties)
    node_columns = ",\n    ".join([sql for sql in node_properties.values()])
    hash_node_columns = ",\n        ".join([f"adapter.quote_as_configured('{column}', 'identifier')" for column in node_properties.keys()])
    hash_node_columns = jinja_call(f"dbt_utils.surrogate_key([\n        {hash_node_columns}\n    ])")
    hash_id = jinja_call(f"adapter.quote_as_configured('_airbyte_{name}_hash', 'identifier')")
    foreign_hash_id = jinja_call(f"adapter.quote_as_configured('_airbyte_{name}_foreign_hash', 'identifier')")
    emitted_col = "{},\n    {} as {}".format(
        jinja_call("adapter.quote_as_configured('_airbyte_emitted_at', 'identifier')"),
        jinja_call("dbt_utils.current_timestamp_in_utc()"),
        jinja_call("adapter.quote_as_configured('_airbyte_normalized_at', 'identifier')"),
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
