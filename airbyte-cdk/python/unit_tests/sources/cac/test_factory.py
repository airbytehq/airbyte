#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import sys
import unittest

import pytest
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory


class AComponentClass:
    def __init__(self, inner_component, value, another_value, vars, config):
        self._inner_component = LowCodeComponentFactory().create_component(inner_component, vars=vars, config=config)
        self._value = value
        self._another_value = another_value
        self._vars = vars
        self._config = config


class InnerComponent:
    def __init__(self, inner_value, vars, config):
        self._inner_value = inner_value
        self._vars = vars
        self._config = config


@pytest.fixture(autouse=True)
def import_module_mock(mocker):
    import_module_mock = mocker.patch("importlib.import_module", lambda m: sys.modules[AComponentClass.__module__])
    yield import_module_mock


def test():
    class_name = f"{AComponentClass.__module__}.{AComponentClass.__name__}"
    options = {
        "inner_component": {
            "class_name": "test_factory.InnerComponent",
            "options": {"inner_value": "inner_val"},
            "vars": {"another_value_from_vars": 1234},
        },
        "value": "Z",
        "another_value": "X",
    }
    vars = {
        "vars_value": "A",
        "vars_value2": "B",
    }
    config = {"config_value": 1, "config_value2": 2}
    parent_vars = {"parent_var": "parent_value"}
    component = LowCodeComponentFactory().build(class_name, options=options, parent_vars=parent_vars, inner_vars=vars, config=config)

    assert component._value == "Z"
    assert component._another_value == "X"
    assert component._vars == {"parent_var": "parent_value", "vars_value": "A", "vars_value2": "B"}
    assert component._config == {"config_value": 1, "config_value2": 2}

    inner_component = component._inner_component
    assert inner_component._inner_value == "inner_val"
    assert inner_component._vars == {"parent_var": "parent_value", "vars_value": "A", "vars_value2": "B", "another_value_from_vars": 1234}
    assert inner_component._config == {"config_value": 1, "config_value2": 2}


if __name__ == "__main__":
    unittest.main()
