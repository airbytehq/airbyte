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
