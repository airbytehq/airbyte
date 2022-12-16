#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from dateutil.relativedelta import relativedelta


@pytest.mark.parametrize(
    "test_name, input_date, date_format, expected_output_date",
    [
        (
            "test_parse_date_iso",
            "2021-01-01T00:00:00.000000+0000",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_timestamp",
            "1609459200",
            "%s",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        ("test_parse_date_number", "20210101", "%Y%m%d", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_date(test_name, input_date, date_format, expected_output_date):
    parser = DatetimeParser()
    output_date = parser.parse(input_date, date_format, datetime.timezone.utc)
    assert expected_output_date == output_date


@pytest.mark.parametrize(
    "test_name, input_dt, datetimeformat, expected_output",
    [
        ("test_format_timestamp", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%s", "1609459200"),
        ("test_format_string", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y-%m-%d", "2021-01-01"),
        ("test_format_to_number", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y%m%d", "20210101"),
    ],
)
def test_format_datetime(test_name, input_dt, datetimeformat, expected_output):
    parser = DatetimeParser()
    output_date = parser.format(input_dt, datetimeformat)
    assert expected_output == output_date


@pytest.mark.parametrize(
    "test_name, datetime_format, expected_output",
    [
        ("test_a_datetime_format", "%Y %W %a", relativedelta(days=1)),
        ("test_A_datetime_format", "%Y %w %A", relativedelta(days=1)),
        ("test_b_datetime_format", "%Y-%b", relativedelta(months=1)),
        ("test_B_datetime_format", "%Y-%B", relativedelta(months=1)),
        ("test_c_datetime_format", "%c", relativedelta(seconds=1)),
        ("test_C_datetime_format", "%C", relativedelta(years=100)),
        ("test_d_datetime_format", "%Y-%m-%d", relativedelta(days=1)),
        ("test_D_datetime_format", "%D", relativedelta(days=1)),
        ("test_e_datetime_format", "%Y-%m-%e", relativedelta(days=1)),
        ("test_f_datetime_format", "%Y-%m-%dT%H:%M:%S %f", relativedelta(microseconds=1)),
        ("test_F_datetime_format", "%F", relativedelta(days=1)),
        ("test_g_datetime_format", "%g", relativedelta(years=1)),
        ("test_G_datetime_format", "%G", relativedelta(years=1)),
        ("test_h_datetime_format", "%Y-%h", relativedelta(months=1)),
        ("test_H_datetime_format", "%Y-%m-%dT%H", relativedelta(hours=1)),
        ("test_I_datetime_format", "%Y-%m-%d %I %p", relativedelta(hours=1)),
        ("test_j_datetime_format", "%Y %j", relativedelta(days=1)),
        ("test_k_datetime_format", "%Y-%m-%dT%k", relativedelta(hours=1)),
        ("test_l_datetime_format", "%Y-%m-%d %l %p", relativedelta(hours=1)),
        ("test_m_datetime_format", "%Y-%m", relativedelta(months=1)),
        ("test_M_datetime_format", "%Y-%m-%dT%H:%M", relativedelta(minutes=1)),
        ("test_r_datetime_format", "%Y-%m-%d %r", relativedelta(seconds=1)),
        ("test_R_datetime_format", "%Y-%m-%d %R", relativedelta(minutes=1)),
        ("test_s_datetime_format", "%s", relativedelta(seconds=1)),
        ("test_S_datetime_format", "%Y-%m-%dT%H:%M:%S", relativedelta(seconds=1)),
        ("test_T_datetime_format", "%Y-%m-%d %T", relativedelta(seconds=1)),
        ("test_u_datetime_format", "%Y %W %u", relativedelta(days=1)),
        ("test_U_datetime_format", "%Y %U", relativedelta(weeks=1)),
        ("test_V_datetime_format", "%Y %V", relativedelta(weeks=1)),
        ("test_w_datetime_format", "%Y %W %w", relativedelta(days=1)),
        ("test_W_datetime_format", "%Y %W", relativedelta(weeks=1)),
        ("test_x_datetime_format", "%x", relativedelta(days=1)),
        ("test_X_datetime_format", "%Y-%m-%d %X", relativedelta(seconds=1)),
        ("test_y_datetime_format", "%C%y", relativedelta(years=1)),
        ("test_Y_datetime_format", "%Y", relativedelta(years=1)),
        ("test_+_datetime_format", "%+", relativedelta(seconds=1)),
    ],
)
def test_find_most_granular_timedelta(test_name, datetime_format, expected_output):
    parser = DatetimeParser()
    output_delta = parser.find_most_granular_timedelta(datetime_format)
    assert output_delta == expected_output


def test_given_most_granular_unit_is_not_parametrized_using_directive_when_find_most_granular_timedelta_then_return_less_granular_delta():
    output_delta = DatetimeParser().find_most_granular_timedelta("%Y-%m-%dT%H:00:00")
    _relativedelta_is_bigger_than(output_delta, datetime.timedelta(seconds=1))


def test_given_no_known_directives_when_find_most_granular_timedelta_then_raise_error():
    with pytest.raises(ValueError):
        DatetimeParser().find_most_granular_timedelta("there is no known directive in this string %q")


def _relativedelta_is_bigger_than(relative_delta: relativedelta, time_delta: datetime.timedelta):
    a_date = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    assert a_date + relative_delta > a_date + time_delta
