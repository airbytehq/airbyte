#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.create_partial import create
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class AClass:
    def __init__(self, parameter, another_param, options):
        self.parameter = parameter
        self.another_param = another_param
        self.options = options


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


def test_overwrite_param():
    object = create(AClass, parameter="A", another_param="B")(parameter="C")
    assert object.parameter == "C"
    assert object.another_param == "B"


def test_string_interpolation():
    s = "{{ next_page_token['next_page_url'] }}"
    partial = create(InterpolatedString, string=s)
    interpolated_string = partial()
    assert interpolated_string.string == s


def test_string_interpolation_through_kwargs():
    s = "{{ options['name'] }}"
    options = {"name": "airbyte"}
    partial = create(InterpolatedString, string=s, **options)
    interpolated_string = partial()
    assert interpolated_string.eval({}) == "airbyte"


def test_string_interpolation_through_options_keyword():
    s = "{{ options['name'] }}"
    options = {"$options": {"name": "airbyte"}}
    partial = create(InterpolatedString, string=s, **options)
    interpolated_string = partial()
    assert interpolated_string.eval({}) == "airbyte"
