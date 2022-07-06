#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

config = {"start": 1234}
kwargs = {"next_page_token": {"next_page_url": "https://airbyte.io"}}


def test_value_is_static():
    static_value = "a_static_value"
    interpolated_string = InterpolatedString(static_value)

    evaluated_string = interpolated_string.eval(config, **kwargs)

    assert evaluated_string == static_value


def test_value_from_config():
    string = "{{ config['start'] }}"
    interpolated_string = InterpolatedString(string)

    evaluated_string = interpolated_string.eval(config, **kwargs)

    assert evaluated_string == config["start"]


def test_value_from_kwargs():
    string = "{{ next_page_token['next_page_url'] }}"
    interpolated_string = InterpolatedString(string)

    evaluated_string = interpolated_string.eval(config, **kwargs)

    assert evaluated_string == "https://airbyte.io"


def test_default_value():
    static_value = "{{ config['end'] }}"
    default = 5678
    interpolated_string = InterpolatedString(static_value, default)

    evaluated_string = interpolated_string.eval(config, **kwargs)

    assert evaluated_string == default


def test_interpolated_default_value():
    static_value = "{{ config['end'] }}"
    interpolated_string = InterpolatedString(static_value, "{{ config['start'] }}")

    evaluated_string = interpolated_string.eval(config, **kwargs)

    assert evaluated_string == config["start"]
