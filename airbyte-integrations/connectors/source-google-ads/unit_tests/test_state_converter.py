# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import date, datetime

from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from source_google_ads.models import CustomerModel
from source_google_ads.state_converter import GadsStateConverter


def test_increment_increases_date_by_one_day():
    converter = GadsStateConverter([])
    initial_date = datetime(2022, 1, 1)
    expected_date = datetime(2022, 1, 2)
    assert converter.increment(initial_date) == expected_date


def test_output_format_returns_string_representation_of_date():
    converter = GadsStateConverter([])
    input_date = date(2022, 1, 1)
    expected_output = "2022-01-01"
    assert converter.output_format(input_date) == expected_output


def test_parse_timestamp_returns_date_when_input_is_date():
    converter = GadsStateConverter([])
    input_date = date(2022, 1, 1)
    assert converter.parse_timestamp(input_date) == input_date


def test_parse_timestamp_parses_string_to_date():
    converter = GadsStateConverter([])
    input_string = "2022-01-01"
    expected_date = date(2022, 1, 1)
    assert converter.parse_timestamp(input_string) == expected_date


def test_deserialize_converts_timestamps_to_dates():
    converter = GadsStateConverter([])
    state = {
        "slices": [
            {"start": "2022-01-01", "end": "2022-01-02"},
        ]
    }
    deserialized_state = converter.deserialize(state)
    assert isinstance(deserialized_state["slices"][0]["start"], date)
    assert isinstance(deserialized_state["slices"][0]["end"], date)


def test_convert_from_sequential_state_creates_slices_for_each_customer():
    customers = [CustomerModel(id="1"), CustomerModel(id="2")]
    converter = GadsStateConverter(customers)
    cursor_field = CursorField("created")
    stream_state = {"1": {"created": "2022-01-01"}, "2": {"created": "2022-01-02"}}
    start = datetime(2022, 1, 1)
    sync_start, concurrent_state = converter.convert_from_sequential_state(cursor_field, stream_state, start)
    assert len(concurrent_state) == len(customers)
    for customer in customers:
        assert customer.id in concurrent_state


def test_convert_to_sequential_state_returns_legacy_state_when_compatible():
    customers = [CustomerModel(id="1")]
    converter = GadsStateConverter(customers)
    cursor_field = CursorField("created")
    stream_state = {
        "1": {
            "state_type": "date_range",
            "slices": [{"start": "2022-01-01", "end": "2022-01-02"}],
            "legacy": {"created": "2022-01-01"},
        }
    }
    new_state = converter.convert_to_sequential_state(cursor_field, stream_state)
    assert new_state["1"]["legacy"]["created"] == "2022-01-01"
