#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from unit_tests.conftest import _YAML_FILE_PATH


def _connection_specification() -> dict:
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config={}, catalog=None, state=None)
    return source.spec(logger=None).connectionSpecification


def test_authentication_renders_before_spreadsheet_link():
    properties = _connection_specification()["properties"]

    assert properties["credentials"]["order"] == 0
    assert properties["spreadsheet_id"]["order"] == 1
    assert properties["credentials"]["order"] < properties["spreadsheet_id"]["order"]


def test_spec_field_orders_are_unique():
    properties = _connection_specification()["properties"]
    orders = [prop["order"] for prop in properties.values() if "order" in prop]

    assert len(orders) == len(set(orders))


def test_spec_declares_groups_and_sections():
    """The stepped setup form: two sections, "Connect spreadsheet" (checked) and "Review & set up" (covered by the full check)."""
    schema = _connection_specification()

    assert [group["id"] for group in schema["groups"]] == ["spreadsheet", "names", "advanced"]
    assert schema["sections"] == [
        {
            "id": "spreadsheet",
            "title": "Connect spreadsheet",
            "order": 0,
            "description": "Sign in with Google and paste the link to the spreadsheet you want to sync.",
            "groups": ["spreadsheet"],
            "check": True,
        },
        {
            "id": "review",
            "title": "Review & set up",
            "order": 1,
            "description": "Name your source and check the optional settings.",
            "groups": ["names", "advanced"],
        },
    ]
    # Every section group is declared, and every property belongs to a group of some section.
    declared_groups = {group["id"] for group in schema["groups"]}
    section_groups = {group for section in schema["sections"] for group in section["groups"]}
    assert section_groups <= declared_groups
    assert {name: prop["group"] for name, prop in schema["properties"].items()} == {
        "credentials": "spreadsheet",
        "spreadsheet_id": "spreadsheet",
        "names_conversion": "names",
        "remove_leading_trailing_underscores": "names",
        "combine_number_word_pairs": "names",
        "remove_special_characters": "names",
        "combine_letter_number_pairs": "names",
        "allow_leading_numbers": "names",
        "read_empty_header_columns": "advanced",
        "stream_name_overrides": "advanced",
        "batch_size": "advanced",
        "num_workers": "advanced",
    }
    # The required fields all belong to the first section, so its check can validate them.
    assert {schema["properties"][name]["group"] for name in schema["required"]} == {"spreadsheet"}
    # The authentication shows as radio tiles; the SQL-compliant names toggle stays visible on the review step.
    assert schema["properties"]["credentials"]["display_type"] == "radio"
    assert schema["properties"]["names_conversion"]["always_show"] is True


def test_spec_orders_properties_as_the_form_shows_them():
    properties = _connection_specification()["properties"]

    orders = {name: prop["order"] for name, prop in properties.items()}
    assert sorted(orders, key=orders.get) == [
        "credentials",
        "spreadsheet_id",
        "names_conversion",
        "remove_leading_trailing_underscores",
        "combine_number_word_pairs",
        "remove_special_characters",
        "combine_letter_number_pairs",
        "allow_leading_numbers",
        "read_empty_header_columns",
        "stream_name_overrides",
        "batch_size",
        "num_workers",
    ]
