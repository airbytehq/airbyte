#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.create_partial import _key_is_unset_or_identical, create
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class AClass:
    def __init__(self, parameter, another_param, parameters):
        self.parameter = parameter
        self.another_param = another_param
        self.parameters = parameters


class OuterClass:
    def __init__(self, name, some_field, inner_param):
        self.name = name
        self.some_field = some_field
        self.inner_param = inner_param


class OuterOuterClass:
    def __init__(self, name, param, inner_class):
        self.name = name
        self.param = param
        self.inner_class = inner_class


def test_pass_parameter_to_create_function():
    object = create(AClass, parameter="A")(another_param="B")
    assert object.parameter == "A"
    assert object.another_param == "B"


def test_parameter_not_overwritten_by_parameters():
    object = create(AClass, parameter="A", another_param="B", **{"$parameters": {"parameter": "C"}})()
    assert object.parameter == "A"
    assert object.another_param == "B"


def test_overwrite_param():
    object = create(AClass, parameter="A", another_param="B")(parameter="C")
    assert object.parameter == "C"
    assert object.another_param == "B"


def test_string_interpolation():
    s = "{{ next_page_token['next_page_url'] }}"
    partial = create(InterpolatedString, string=s)
    interpolated_string = partial()
    assert interpolated_string.string == s


def test_string_interpolation_through_parameters():
    s = "{{ parameters['name'] }}"
    parameters = {"name": "airbyte"}
    partial = create(InterpolatedString, string=s, **parameters)
    interpolated_string = partial()
    assert interpolated_string.eval({}) == "airbyte"


def test_string_interpolation_through_parameters_keyword():
    s = "{{ parameters['name'] }}"
    parameters = {"$parameters": {"name": "airbyte"}}
    partial = create(InterpolatedString, string=s, **parameters)
    interpolated_string = partial()
    assert interpolated_string.eval({}) == "airbyte"


@pytest.mark.parametrize(
    "test_name, key, value, expected_result",
    [
        ("test", "key", "value", True),
        ("test", "key", "a_different_value", False),
        ("test", "a_different_key", "value", True),
    ],
)
def test_key_is_unset_or_identical(test_name, key, value, expected_result):
    mapping = {"key": "value"}
    result = _key_is_unset_or_identical(key, value, mapping)
    assert expected_result == result
