#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.states.dict_state import DictState, StateType

config = {"name": "date"}
name = "{{ config['name'] }}"
value = "{{ last_record['updated_at'] }}"
dict_mapping = {
    name: value,
}


def test_empty_state_is_none():
    state = DictState(dict_mapping, "INT", config)
    initial_state = state.get_stream_state()
    expected_state = {}
    assert expected_state == initial_state


def test_state_type():
    state_type_string = DictState(dict_mapping, "INT", config)
    state_type_type = DictState(dict_mapping, int, config)
    state_type_enum = DictState(dict_mapping, StateType.INT, config)
    assert state_type_string._state_type == state_type_type._state_type == state_type_enum._state_type


def test_update_initial_state():
    state = DictState(dict_mapping, "STR", config)
    stream_slice = None
    stream_state = None
    last_response = {"data": {"id": "1234", "updated_at": "2021-01-01"}, "last_refresh": "2020-01-01"}
    last_record = {"id": "1234", "updated_at": "2021-01-01"}
    state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=last_response, last_record=last_record)
    actual_state = state.get_stream_state()
    expected_state = {"date": "2021-01-01"}
    assert expected_state == actual_state


def test_update_state_with_recent_cursor():
    state = DictState(dict_mapping, "STR", config)
    stream_slice = None
    stream_state = {"date": "2020-12-31"}
    last_response = {"data": {"id": "1234", "updated_at": "2021-01-01"}, "last_refresh": "2020-01-01"}
    last_record = {"id": "1234", "updated_at": "2021-01-01"}
    state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=last_response, last_record=last_record)
    actual_state = state.get_stream_state()
    expected_state = {"date": "2021-01-01"}
    assert expected_state == actual_state


def test_update_state_with_old_cursor():
    state = DictState(dict_mapping, "STR", config)
    stream_slice = None
    stream_state = {"date": "2021-01-02"}
    last_response = {"data": {"id": "1234", "updated_at": "2021-01-01"}, "last_refresh": "2020-01-01"}
    last_record = {"id": "1234", "updated_at": "2021-01-01"}
    state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=last_response, last_record=last_record)
    actual_state = state.get_stream_state()
    expected_state = {"date": "2021-01-02"}
    assert expected_state == actual_state


def test_update_state_with_older_state():
    state = DictState(dict_mapping, "STR", config)
    stream_slice = None
    stream_state = {"date": "2021-01-02"}
    last_response = {"data": {"id": "1234", "updated_at": "2021-01-02"}, "last_refresh": "2020-01-01"}
    last_record = {"id": "1234", "updated_at": "2021-01-02"}
    state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=last_response, last_record=last_record)
    actual_state = state.get_stream_state()
    expected_state = {"date": "2021-01-02"}

    out_of_order_response = {"data": {"id": "1234", "updated_at": "2021-01-02"}, "last_refresh": "2020-01-01"}
    out_of_order_record = {"id": "1234", "updated_at": "2021-01-01"}
    state.update_state(
        stream_slice=stream_slice, stream_state=stream_state, last_response=out_of_order_response, last_record=out_of_order_record
    )
    assert expected_state == actual_state


def test_state_is_a_timestamp():
    state = DictState(dict_mapping, "INT", config)
    stream_slice = None
    stream_state = {"date": 12345}
    last_response = {"data": {"id": "1234", "updated_at": 123456}, "last_refresh": "2020-01-01"}
    last_record = {"id": "1234", "updated_at": 123456}
    state.update_state(stream_slice=stream_slice, stream_state=stream_state, last_response=last_response, last_record=last_record)
    actual_state = state.get_stream_state()
    expected_state = {"date": 123456}
    assert expected_state == actual_state
