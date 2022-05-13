#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.lcc.create_partial import create


class AClass:
    def __init__(self, parameter, another_param):
        self.parameter = parameter
        self.another_param = another_param


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


def test_interpolation_from_another_parameter():
    object = create(AClass, parameter="A")(another_param="{{ kwargs['parameter'] }}")
    assert object.parameter == "A"
    assert object.another_param == "A"


def test_propagate_kwargs():
    inner_object = create(AClass, parameter="I", another_param="{{ kwargs['name'] }}")
    object = create(OuterClass, some_field="A", inner_param=inner_object)(kwargs={"name": "AIRBYTE"})
    assert object.name == "AIRBYTE"
    assert object.some_field == "A"
    assert object.inner_param.parameter == "I"
    assert object.inner_param.another_param == "AIRBYTE"


def test_propagate_kwargs_2_levels_down():
    inner_object = create(AClass, parameter="I", another_param="{{ kwargs['name'] }}")
    object = create(OuterClass, some_field="A", inner_param=inner_object)
    outer_object = create(OuterOuterClass, inner_class=object)(kwargs={"name": "AIRBYTE", "param": "param"})
    assert outer_object.inner_class.name == "AIRBYTE"
    assert outer_object.inner_class.some_field == "A"
    assert outer_object.inner_class.inner_param.parameter == "I"
    assert outer_object.inner_class.inner_param.another_param == "AIRBYTE"
    assert outer_object.name == "AIRBYTE"
    assert outer_object.param == "param"
