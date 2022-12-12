#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# This script is not actually part of the source connector. Instead, this script automatically generates the
# json schemas and class source definitions.
# This is done by scraping the documentation pages using requests + beautifulsoup.

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class TableRow:
    service: str
    endpoint_url: str
    documentation_url: str


def parse_url(url: str) -> BeautifulSoup:
    """Retrieves page using requests and parses the page using BeautifulSoup."""

    response = requests.get(url)
    response.raise_for_status()

    return BeautifulSoup(response.content, "html.parser")


def pascal_to_snake(input: str) -> str:
    source_name_snake = re.sub(r"[A-Z]([A-Z](?![a-z]))*", lambda x: "_" + x.group(0), input)
    source_name_snake = source_name_snake.lower()
    source_name_snake = source_name_snake.strip("_")
    source_name_snake = source_name_snake.replace("__", "_")

    return source_name_snake


def parse_table_row_from_html(row: Tag) -> list[TableRow]:
    """
    Parses single table row from HTML. Returns only records for Sync endpoints. Other endpoints are ignored and None
    is returned.

    Expected input page: https://start.exactonline.nl/docs/HlpRestAPIResources.aspx
    """

    service, endpoint, resource_uri, methods, _, _ = row.select("td")
    service = service.text
    resource_uri = resource_uri.text
    methods = methods.text

    # Skip non sync gettable endpoints
    if "GET" not in methods or service != "Sync" or not resource_uri.startswith("/api"):
        return None

    if not resource_uri.startswith("/api"):
        return None

    endpoint = endpoint.select_one("a.Endpoints")
    if not endpoint:
        raise RuntimeError(f"Failed to get endpoint details for {resource_uri}")

    href = endpoint.attrs["href"]
    url = f"https://start.exactonline.nl/docs/{href}"

    return TableRow(service, resource_uri, url)


def parse_json_schema_from_table_row(table_row: TableRow) -> dict:
    """
    Given endpoint row from the main documentation page (TableRow), retrieve the endpoint page and generate
    the json schema.
    """

    soup = parse_url(table_row.documentation_url)
    title = table_row.service + soup.select_one('p#endpoint').text.strip().replace("/", "")

    soup_table = soup.select_one("table#referencetable")

    # Some descriptions contain additional tables.
    # For instance enum fields: https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SyncFinancialTransactionLines
    # This doesn't parse well so we just remove all nested tables
    for nested_table in soup_table.find_all("table"):
        nested_table.extract()

    df_properties = pd.read_html(str(soup_table), flavor="bs4")[0]
    df_properties.columns = [x.replace("↑↓", "").strip() for x in df_properties.columns]

    # Lookup to map OData types to their JSON Schema counter part
    json_type_lookup = {
        "Boolean": "boolean",
        "DateTime": {
            "type": "string",
            "format": "date-time",
        },
        "Time": {
            "type": "string",
            "format": "time",
        },
        "Double": "number",
        "Byte": "integer",
        "Int8": "integer",
        "Int16": "integer",
        "Int32": "integer",
        "Int64": "integer",
        "String": "string",
        "Guid": "string",
    }

    json_properties = {}
    for row in df_properties.itertuples():
        name = row.Name.strip()
        type_ = row.Type.replace("Edm.", "").strip()
        description = row.Description.strip()

        json_type = json_type_lookup.get(type_)
        if json_type is None:
            print(f"Skipping property '{name}', unknown type '{type_}' (endpoint: {title})")
            # raise RuntimeError(f"Missing type lookup for '{type_}' (name: {name}, title: {title})")
            continue

        # Create JSON Schema property
        json_property = {
            "description": description,
        }

        if isinstance(json_type, str):
            json_property["type"] = json_type
        else:
            json_property.update(json_type)

        json_properties[name] = json_property

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": title,
        # NOTE: descriptions are really extensive, not sure if they add a lot so for now disabled them
        # "description": soup.select_one("p#goodToKnow").text.strip(),
        "properties": json_properties,
    }


def write_json_schema_file(json_schema: dict):
    """Write json schema to schemas/ directory."""

    source_name_pascal = json_schema["title"].replace("/", "_")
    source_name_snake = pascal_to_snake(source_name_pascal)

    current_dir = os.path.dirname(__file__)

    json_schema_path = os.path.join(current_dir, "schemas", f"{source_name_snake}.json")
    with open(json_schema_path, "w") as f:
        json.dump(json_schema, f, indent=2)


def generate_class_definition(json_schema: dict) -> str:
    """Generate class definition for source stream."""

    source_name_pascal = json_schema["title"].replace("/", "")

    return f"""
class {source_name_pascal}(ExactStream):
    primary_key = "Timestamp"
    endpoint = "{json_schema['title']}"
    """.strip()


def main():
    soup_root = parse_url("https://start.exactonline.nl/docs/HlpRestAPIResources.aspx")
    soup_rows = soup_root.select("table#referencetable tr.filter")

    table_rows = [parse_table_row_from_html(x) for x in soup_rows]
    table_rows = [x for x in table_rows if x is not None]

    def handle_endpoint(table_row: TableRow):
        try:
            json_schema = parse_json_schema_from_table_row(table_row)
            write_json_schema_file(json_schema)

            class_definition = generate_class_definition(json_schema)
            return class_definition
        except Exception as exc:
            raise RuntimeError(f"Error handling endpoint '{table_row.endpoint_url}'") from exc

    with ThreadPoolExecutor(max_workers=8) as pool:
        class_definitions = list(pool.map(handle_endpoint, table_rows))
        print("Class definitions\n")
        print("\n\n".join(class_definitions))


if __name__ == "__main__":
    main()
