#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from freezegun import freeze_time
from jinja2.exceptions import TemplateSyntaxError

interpolation = JinjaInterpolation()


def test_get_value_from_config():
    s = "{{ config['date'] }}"
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, config)
    assert val == "2022-01-01"


def test_get_missing_value_from_config():
    s = "{{ config['date'] }}"
    config = {}
    val = interpolation.eval(s, config)
    assert val is None


@pytest.mark.parametrize(
    "valid_types, expected_value",
    [
        pytest.param((str,), "1234J", id="test_value_is_a_string_if_valid_types_is_str"),
        pytest.param(None, 1234j, id="test_value_is_interpreted_as_complex_number_by_default"),
    ],
)
def test_get_value_with_complex_number(valid_types, expected_value):
    s = "{{ config['value'] }}"
    config = {"value": "1234J"}
    val = interpolation.eval(s, config, valid_types=valid_types)
    assert val == expected_value


def test_get_value_from_stream_slice():
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"


def test_get_missing_value_from_stream_slice():
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val is None


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
    "test_name, input_value, expected_output",
    [
        ("test_string_to_string", "hello world", "hello world"),
        ("test_int_to_string", 1, "1"),
        ("test_number_to_string", 1.52, "1.52"),
        ("test_true_to_string", True, "true"),
        ("test_false_to_string", False, "false"),
        ("test_array_to_string", ["hello", "world"], '["hello", "world"]'),
        ("test_object_to_array", {"hello": "world"}, '{"hello": "world"}'),
    ],
)
def test_to_string(test_name, input_value, expected_output):
    interpolation = JinjaInterpolation()
    config = {"key": input_value}
    template = "{{ config['key'] | string }}"
    actual_output = interpolation.eval(template, config, {})
    assert isinstance(actual_output, str)
    assert actual_output == expected_output


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


@freeze_time("2021-09-01")
@pytest.mark.parametrize(
    "template_string, expected_value",
    [
        pytest.param("{{ now_utc() }}", "2021-09-01 00:00:00+00:00", id="test_now_utc"),
        pytest.param("{{ now_utc().strftime('%Y-%m-%d') }}", "2021-09-01", id="test_now_utc_strftime"),
        pytest.param("{{ today_utc() }}", "2021-09-01", id="test_today_utc"),
        pytest.param("{{ today_utc().strftime('%Y/%m/%d') }}", "2021/09/01", id="test_todat_utc_stftime"),
        pytest.param("{{ timestamp(1646006400) }}", 1646006400, id="test_timestamp_from_timestamp"),
        pytest.param("{{ timestamp('2022-02-28') }}", 1646006400, id="test_timestamp_from_timestamp"),
        pytest.param("{{ timestamp('2022-02-28T00:00:00Z') }}", 1646006400, id="test_timestamp_from_timestamp"),
        pytest.param("{{ timestamp('2022-02-28 00:00:00Z') }}", 1646006400, id="test_timestamp_from_timestamp"),
        pytest.param("{{ timestamp('2022-02-28T00:00:00-08:00') }}", 1646035200, id="test_timestamp_from_date_with_tz"),
        pytest.param("{{ max(2, 3) }}", 3, id="test_max_with_arguments"),
        pytest.param("{{ max([2, 3]) }}", 3, id="test_max_with_list"),
        pytest.param("{{ day_delta(1) }}", "2021-09-02T00:00:00.000000+0000", id="test_day_delta"),
        pytest.param("{{ day_delta(-1) }}", "2021-08-31T00:00:00.000000+0000", id="test_day_delta_negative"),
        pytest.param("{{ day_delta(1, format='%Y-%m-%d') }}", "2021-09-02", id="test_day_delta_with_format"),
        pytest.param("{{ duration('P1D') }}", "1 day, 0:00:00", id="test_duration_one_day"),
        pytest.param("{{ duration('P6DT23H') }}", "6 days, 23:00:00", id="test_duration_six_days_and_23_hours"),
        pytest.param(
            "{{ (now_utc() - duration('P1D')).strftime('%Y-%m-%dT%H:%M:%SZ') }}",
            "2021-08-31T00:00:00Z",
            id="test_now_utc_with_duration_and_format",
        ),
        pytest.param("{{ 1 | string }}", "1", id="test_int_to_string"),
        pytest.param('{{ ["hello", "world"] | string }}', '["hello", "world"]', id="test_array_to_string"),
    ],
)
def test_macros_examples(template_string, expected_value):
    # The outputs of this test are referenced in declarative_component_schema.yaml
    # If you change the expected output, you must also change the expected output in declarative_component_schema.yaml
    now_utc = interpolation.eval(template_string, {})
    assert now_utc == expected_value


def test_interpolation_private_partition_attribute():
    inner_partition = StreamSlice(partition={}, cursor_slice={})
    expected_output = "value"
    setattr(inner_partition, "parent_stream_fields", expected_output)
    stream_slice = StreamSlice(partition=inner_partition, cursor_slice={})
    template = "{{ stream_slice._partition.parent_stream_fields }}"

    actual_output = JinjaInterpolation().eval(template, {}, **{"stream_slice": stream_slice})

    assert actual_output == expected_output
