#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from pathlib import Path

import yaml


DEPRECATED_PAGE_FIELDS = [
    "current_location",
    "genre",
    "network",
    "parking",
    "start_info",
]
SCHEMAS_PATH = Path(__file__).parents[1] / "source_facebook_pages" / "schemas"


def _load_page_property_list():
    manifest_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "source_facebook_pages",
        "manifest.yaml",
    )
    with open(manifest_path) as manifest_file:
        manifest = yaml.safe_load(manifest_file)
    return manifest["definitions"]["page_query_properties"]["property_list"]


def _load_schema_properties(schema_name):
    schema = json.loads((SCHEMAS_PATH / schema_name).read_text())
    return schema["properties"]


def test_page_request_omits_deprecated_fields():
    property_list = _load_page_property_list()
    deprecated_fields = set(property_list) & set(DEPRECATED_PAGE_FIELDS)
    assert not deprecated_fields, f"Deprecated fields still requested: {sorted(deprecated_fields)}"


def test_page_request_still_includes_supported_fields():
    property_list = _load_page_property_list()
    supported_fields = {"id", "name", "about", "category"}
    assert supported_fields <= set(property_list)


def test_page_schemas_omit_deprecated_fields():
    page_properties = _load_schema_properties("page.json")
    shared_page_properties = _load_schema_properties("shared/page.json")
    deprecated_fields = set(DEPRECATED_PAGE_FIELDS)

    assert not deprecated_fields & set(page_properties)
    assert not deprecated_fields & set(shared_page_properties)
    assert {"id", "name", "about"} <= set(page_properties)
