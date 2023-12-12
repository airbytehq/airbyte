#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import sys
from unittest.mock import Mock, mock_open, patch

import pytest
from source_google_analytics_data_api.utils import (
    get_source_defined_primary_key,
    serialize_to_date_string,
    transform_between_filter,
    transform_expression,
    transform_in_list_filter,
    transform_json,
    transform_numeric_filter,
    transform_string_filter,
)


class TestSerializeToDateString:
    @pytest.mark.parametrize(
        "input_date, date_format, date_type, expected",
        [
            ("202105", "%Y-%m-%d", "yearWeek", "2021-02-01"),
            ("202105", "%Y-%m-%d", "yearMonth", "2021-05-01"),
            ("202245", "%Y-%m-%d", "yearWeek", "2022-11-07"),
            ("202210", "%Y-%m-%d", "yearMonth", "2022-10-01"),
            ("2022", "%Y-%m-%d", "year", "2022-01-01"),
        ],
    )
    def test_valid_cases(self, input_date, date_format, date_type, expected):
        result = serialize_to_date_string(input_date, date_format, date_type)
        assert result == expected

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            serialize_to_date_string("202105", "%Y-%m-%d", "invalidType")


class TestTransformFilters:
    def test_transform_string_filter(self):
        filter_data = {"value": "test", "matchType": ["partial"], "caseSensitive": True}
        expected = {"stringFilter": {"value": "test", "matchType": "partial", "caseSensitive": True}}
        result = transform_string_filter(filter_data)
        assert result == expected

    def test_transform_in_list_filter(self):
        filter_data = {"values": ["test1", "test2"], "caseSensitive": False}
        expected = {"inListFilter": {"values": ["test1", "test2"], "caseSensitive": False}}
        result = transform_in_list_filter(filter_data)
        assert result == expected

    def test_transform_numeric_filter(self):
        filter_data = {"value": {"value_type": "doubleValue", "value": 5.5}, "operation": ["equals"]}
        expected = {"numericFilter": {"value": {"doubleValue": 5.5}, "operation": "equals"}}
        result = transform_numeric_filter(filter_data)
        assert result == expected

    @pytest.mark.parametrize(
        "filter_data, expected",
        [
            (
                {"fromValue": {"value_type": "doubleValue", "value": "10.5"}, "toValue": {"value_type": "doubleValue", "value": "20.5"}},
                {"betweenFilter": {"fromValue": {"doubleValue": 10.5}, "toValue": {"doubleValue": 20.5}}},
            ),
            (
                {"fromValue": {"value_type": "stringValue", "value": "hello"}, "toValue": {"value_type": "stringValue", "value": "world"}},
                {"betweenFilter": {"fromValue": {"stringValue": "hello"}, "toValue": {"stringValue": "world"}}},
            ),
            (
                {"fromValue": {"value_type": "doubleValue", "value": 10.5}, "toValue": {"value_type": "doubleValue", "value": 20.5}},
                {"betweenFilter": {"fromValue": {"doubleValue": 10.5}, "toValue": {"doubleValue": 20.5}}},
            ),
        ],
    )
    def test_transform_between_filter(self, filter_data, expected):
        result = transform_between_filter(filter_data)
        assert result == expected


class TestTransformExpression:
    @patch("source_google_analytics_data_api.utils.transform_string_filter", Mock(return_value={"stringFilter": "mocked_string_filter"}))
    @patch("source_google_analytics_data_api.utils.transform_in_list_filter", Mock(return_value={"inListFilter": "mocked_in_list_filter"}))
    @patch("source_google_analytics_data_api.utils.transform_numeric_filter", Mock(return_value={"numericFilter": "mocked_numeric_filter"}))
    def test_between_filter(self):
        expression = {
            "field_name": "some_field",
            "filter": {
                "filter_name": "betweenFilter",
                "fromValue": {"value_type": "doubleValue", "value": "10.5"},
                "toValue": {"value_type": "doubleValue", "value": "20.5"},
            },
        }
        expected = {
            "filter": {"fieldName": "some_field", "betweenFilter": {"fromValue": {"doubleValue": 10.5}, "toValue": {"doubleValue": 20.5}}}
        }
        result = transform_expression(expression)
        assert result == expected


class TestGetSourceDefinedPrimaryKey:
    @pytest.mark.parametrize(
        "stream_name, mocked_content, expected",
        [
            ("sample_stream", {"streams": [{"stream": {"name": "sample_stream", "source_defined_primary_key": ["id"]}}]}, ["id"]),
            ("sample_stream", {"streams": [{"stream": {"name": "different_stream", "source_defined_primary_key": ["id"]}}]}, None),
        ],
    )
    def test_primary_key(self, stream_name, mocked_content, expected):
        sys.argv = ["script_name", "read", "--catalog", "mocked_catalog_path"]
        m = mock_open(read_data=json.dumps(mocked_content))
        with patch("builtins.open", m):
            with patch("json.loads", return_value=mocked_content):
                result = get_source_defined_primary_key(stream_name)
        assert result == expected


class TestTransformJson:
    @staticmethod
    def mock_transform_expression(expression):
        return {"transformed": expression}

    # Applying pytest monkeypatch for the mock_transform_expression
    @pytest.fixture(autouse=True)
    def mock_transform_functions(self, monkeypatch):
        monkeypatch.setattr("source_google_analytics_data_api.utils.transform_expression", self.mock_transform_expression)

    @pytest.mark.parametrize(
        "original, expected",
        [
            (
                {
                    "filter_type": "andGroup",
                    "expressions": [{"field": "field1", "condition": "cond1"}, {"field": "field2", "condition": "cond2"}],
                },
                {
                    "andGroup": {
                        "expressions": [
                            {"transformed": {"field": "field1", "condition": "cond1"}},
                            {"transformed": {"field": "field2", "condition": "cond2"}},
                        ]
                    }
                },
            ),
            (
                {"filter_type": "orGroup", "expressions": [{"field": "field1", "condition": "cond1"}]},
                {"orGroup": {"expressions": [{"transformed": {"field": "field1", "condition": "cond1"}}]}},
            ),
            (
                {"filter_type": "notExpression", "expression": {"field": "field1", "condition": "cond1"}},
                {"notExpression": {"transformed": {"field": "field1", "condition": "cond1"}}},
            ),
            (
                {"filter_type": "filter", "field": "field1", "condition": "cond1"},
                {"transformed": {"condition": "cond1", "field": "field1", "filter_type": "filter"}},
            ),
            ({"filter_type": "andGroup"}, {}),
        ],
    )
    def test_cases(self, original, expected):
        result = transform_json(original)
        assert result == expected
