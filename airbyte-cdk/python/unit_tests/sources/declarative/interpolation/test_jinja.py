#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from freezegun import freeze_time
from jinja2.exceptions import TemplateSyntaxError

interpolation = JinjaInterpolation()


def test_get_value_from_config():
    s = "{{ config['date'] }}"
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, config)
    assert val == "2022-01-01"


def test_get_value_from_stream_slice():
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"


def test_get_value_from_a_list_of_mappings():
    s = "{{ records[0]['date'] }}"
    config = {"date": "2022-01-01"}
    records = [{"date": "2020-09-09"}]
    val = interpolation.eval(s, config, **{"records": records})
    assert val == "2020-09-09"


@pytest.mark.parametrize(
    "s, value",
    [
        pytest.param("{{1}}", 1, id="test_number"),
        pytest.param("{{1}}", 1, id="test_number"),
        pytest.param("{{[1,2]}}", [1, 2], id="test_list"),
        pytest.param("{{ {1:2} }}", {1: 2}, id="test_dict"),
        pytest.param("{{ 1+2 }}", 3, id="test_addition"),
    ],
)
def test_literals(s, value):
    val = interpolation.eval(s, None)
    assert val == value


@pytest.mark.parametrize(
    "context, input_string, expected_value",
    [
        pytest.param(
            {"stream_slice": {"stream_slice_key": "hello"}},
            "{{ stream_slice['stream_slice_key'] }}",
            "hello",
            id="test_get_value_from_stream_slice",
        ),
        pytest.param(
            {"stream_slice": {"stream_slice_key": "hello"}},
            "{{ stream_partition['stream_slice_key'] }}",
            "hello",
            id="test_get_value_from_stream_slicer",
        ),
        pytest.param(
            {"stream_slice": {"stream_slice_key": "hello"}},
            "{{ stream_interval['stream_slice_key'] }}",
            "hello",
            id="test_get_value_from_stream_interval",
        ),
    ],
)
def test_stream_slice_alias(context, input_string, expected_value):
    config = {}
    val = interpolation.eval(input_string, config, **context)
    assert val == expected_value


@pytest.mark.parametrize(
    "alias",
    [
        pytest.param("stream_interval", id="test_error_is_raised_if_stream_interval_in_context"),
        pytest.param("stream_partition", id="test_error_is_raised_if_stream_partition_in_context"),
    ],
)
def test_error_is_raised_if_alias_is_already_in_context(alias):
    config = {}
    context = {alias: "a_value"}
    with pytest.raises(ValueError):
        interpolation.eval("a_key", config, **context)


def test_positive_day_delta():
    delta_template = "{{ day_delta(25) }}"
    interpolation = JinjaInterpolation()
    val = interpolation.eval(delta_template, {})

    # We need to assert against an earlier delta since the interpolation function runs datetime.now() a few milliseconds earlier
    assert val > (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=24, hours=23)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def test_positive_day_delta_with_format():
    delta_template = "{{ day_delta(25,format='%Y-%m-%d') }}"

    with freeze_time("2021-01-01 03:04:05"):
        val = interpolation.eval(delta_template, {})
        assert val == "2021-01-26"


def test_negative_day_delta():
    delta_template = "{{ day_delta(-25) }}"
    val = interpolation.eval(delta_template, {})

    assert val <= (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=25)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


@pytest.mark.parametrize(
    "s, expected_value",
    [
        pytest.param("{{ timestamp(1621439283) }}", 1621439283, id="test_timestamp_from_timestamp"),
        pytest.param("{{ timestamp('2021-05-19') }}", 1621382400, id="test_timestamp_from_string"),
        pytest.param("{{ timestamp('2017-01-01T00:00:00.0Z') }}", 1483228800, id="test_timestamp_from_rfc3339"),
        pytest.param("{{ max(1,2) }}", 2, id="test_max"),
    ],
)
def test_macros(s, expected_value):
    config = {}
    val = interpolation.eval(s, config)
    assert val == expected_value


@pytest.mark.parametrize(
    "template_string",
    [
        pytest.param("{{ import os) }}", id="test_jinja_with_import"),
        pytest.param("{{ [a for a in range(1000000000)] }}", id="test_jinja_with_list_comprehension"),
    ],
)
def test_invalid_jinja_statements(template_string):
    config = {"key": "value"}
    with pytest.raises(TemplateSyntaxError):
        interpolation.eval(template_string, config=config)


@pytest.mark.parametrize(
    "template_string",
    [
        # This test stalls if range is removed from JinjaInterpolation.RESTRICTED_BUILTIN_FUNCTIONS
        pytest.param(
            """
       {% set a = 1 %}
       {% set b = 1 %}
       {% for i in range(1000000000) %}
       {% endfor %}
        {{ a }}""",
            id="test_jinja_with_very_long_running_compute",
        ),
        pytest.param("{{ eval ('2+2') }}", id="test_jinja_with_eval"),
        pytest.param("{{ getattr(config, 'key') }}", id="test_getattr"),
        pytest.param("{{ setattr(config, 'password', 'hunter2') }}", id="test_setattr"),
        pytest.param("{{ globals()  }}", id="test_jinja_with_globals"),
        pytest.param("{{ locals()  }}", id="test_jinja_with_globals"),
        pytest.param("{{ eval ('2+2') }}", id="test_jinja_with_eval"),
        pytest.param("{{ eval }}", id="test_jinja_with_eval"),
    ],
)
def test_restricted_builtin_functions_are_not_executed(template_string):
    config = {"key": JinjaInterpolation}
    with pytest.raises(ValueError):
        interpolation.eval(template_string, config=config)


@pytest.mark.parametrize(
    "template_string, expected_value, expected_error",
    [
        pytest.param("{{ to_be }}", "that_is_the_question", None, id="valid_template_variable"),
        pytest.param("{{ missingno }}", None, ValueError, id="undeclared_template_variable"),
        pytest.param("{{ to_be and or_not_to_be }}", None, ValueError, id="one_undeclared_template_variable"),
    ],
)
def test_undeclared_variables(template_string, expected_error, expected_value):
    config = {"key": JinjaInterpolation}

    if expected_error:
        with pytest.raises(expected_error):
            interpolation.eval(template_string, config=config, **{"to_be": "that_is_the_question"})
    else:
        actual_value = interpolation.eval(template_string, config=config, **{"to_be": "that_is_the_question"})
        assert actual_value == expected_value
