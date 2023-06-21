#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List

import pytest
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage
from airbyte_cdk.utils.datetime_format_inferrer import DatetimeFormatInferrer

NOW = 1234567


@pytest.mark.parametrize(
    "test_name,input_records,expected_candidate_fields",
    [
        ("empty", [], {}),
        ("simple_match", [{"d": "2022-02-03"}], {"d": "%Y-%m-%d"}),
        ("timestamp_match_integer", [{"d": 1686058051}], {"d": "%s"}),
        ("timestamp_match_string", [{"d": "1686058051"}], {"d": "%s"}),
        ("timestamp_no_match_integer", [{"d": 99}], {}),
        ("timestamp_no_match_string", [{"d": "99999999999999999999"}], {}),
        ("simple_no_match", [{"d": "20220203"}], {}),
        ("multiple_match", [{"d": "2022-02-03", "e": "2022-02-03"}], {"d": "%Y-%m-%d", "e": "%Y-%m-%d"}),
        (
            "multiple_no_match",
            [{"d": "20220203", "r": "ccc", "e": {"something-else": "2023-03-03"}, "s": ["2023-03-03"], "x": False, "y": 123}],
            {},
        ),
        ("format_1", [{"d": "2022-02-03"}], {"d": "%Y-%m-%d"}),
        ("format_2", [{"d": "2022-02-03 12:34:56"}], {"d": "%Y-%m-%d %H:%M:%S"}),
        ("format_3", [{"d": "2022-02-03 12:34:56.123456+00:00"}], {"d": "%Y-%m-%d %H:%M:%S.%f%z"}),
        ("format_3 2", [{"d": "2022-02-03 12:34:56.123456+02:00"}], {"d": "%Y-%m-%d %H:%M:%S.%f%z"}),
        ("format_4", [{"d": "2022-02-03T12:34:56.123456+0000"}], {"d": "%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("format_4 2", [{"d": "2022-02-03T12:34:56.000Z"}], {"d": "%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("format_4 3", [{"d": "2022-02-03T12:34:56.000000Z"}], {"d": "%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("format_4 4", [{"d": "2022-02-03T12:34:56.123456+00:00"}], {"d": "%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("format_4 5", [{"d": "2022-02-03T12:34:56.123456-03:00"}], {"d": "%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("format_6", [{"d": "03/02/2022 12:34"}], {"d": "%d/%m/%Y %H:%M"}),
        ("format_7", [{"d": "2022-02"}], {"d": "%Y-%m"}),
        ("format_8", [{"d": "03-02-2022"}], {"d": "%d-%m-%Y"}),
        ("limit_down", [{"d": "2022-02-03", "x": "2022-02-03"}, {"d": "2022-02-03", "x": "another thing"}], {"d": "%Y-%m-%d"}),
        ("limit_down all", [{"d": "2022-02-03", "x": "2022-02-03"}, {"d": "also another thing", "x": "another thing"}], {}),
        ("limit_down empty", [{"d": "2022-02-03", "x": "2022-02-03"}, {}], {}),
        ("limit_down unsupported type", [{"d": "2022-02-03"}, {"d": False}], {}),
        ("limit_down complex type", [{"d": "2022-02-03"}, {"d": {"date": "2022-03-03"}}], {}),
        ("limit_down different format", [{"d": "2022-02-03"}, {"d": 1686058051}], {}),
        ("limit_down different format", [{"d": "2022-02-03"}, {"d": "2022-02-03T12:34:56.000000Z"}], {}),
        ("no scope expand", [{}, {"d": "2022-02-03"}], {}),
    ],
)
def test_schema_inferrer(test_name, input_records: List, expected_candidate_fields: Dict[str, str]):
    inferrer = DatetimeFormatInferrer()
    for record in input_records:
        inferrer.accumulate(AirbyteRecordMessage(stream="abc", data=record, emitted_at=NOW))
    assert inferrer.get_inferred_datetime_formats() == expected_candidate_fields
