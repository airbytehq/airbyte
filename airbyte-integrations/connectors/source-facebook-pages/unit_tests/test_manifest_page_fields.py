#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import yaml


DEPRECATED_PAGE_FIELDS = [
    "current_location",
    "genre",
    "network",
    "parking",
    "start_info",
]


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


def test_page_request_omits_deprecated_fields():
    property_list = _load_page_property_list()
    deprecated_fields = set(property_list) & set(DEPRECATED_PAGE_FIELDS)
    assert not deprecated_fields, f"Deprecated fields still requested: {sorted(deprecated_fields)}"


def test_page_request_still_includes_supported_fields():
    property_list = _load_page_property_list()
    supported_fields = {"id", "name", "about", "category"}
    assert supported_fields <= set(property_list)
