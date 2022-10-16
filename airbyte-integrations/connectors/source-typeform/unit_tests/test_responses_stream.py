#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pendulum
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from pendulum.datetime import DateTime
from source_typeform.source import Responses

config = {"token": "10", "start_date": "2020-06-27T15:32:38Z", "page_size": 2}

UTC = pendulum.timezone("UTC")
responses = Responses(authenticator=TokenAuthenticator(token=config["token"]), **config)


def get_last_record(last_record_cursor: DateTime, form_id: str = "form1") -> str:
    metadata = {"referer": f"http://134/{form_id}"} if form_id else {}
    return {Responses.cursor_field: last_record_cursor.format(Responses.date_format), "metadata": metadata}


def test_get_updated_state_new():
    # current record cursor greater than current state
    current_state = {"form1": {Responses.cursor_field: 100000}}
    last_record_cursor = pendulum.now(UTC)
    last_record = get_last_record(last_record_cursor)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] == last_record_cursor.int_timestamp


def test_get_updated_state_not_changed():
    # current record cursor less than current state
    current_state = {"form1": {Responses.cursor_field: 100000}}
    last_record_cursor = pendulum.from_timestamp(100)
    last_record = get_last_record(last_record_cursor)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] != last_record_cursor.int_timestamp
    assert new_state["form1"][Responses.cursor_field] == 100000


def test_get_updated_state_form_id_is_new():
    # current record has new form id which is not exists in current state
    current_state = {"form1": {Responses.cursor_field: 100000}}
    last_record_cursor = pendulum.from_timestamp(100)
    last_record = get_last_record(last_record_cursor, form_id="form2")

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form2"][Responses.cursor_field] == last_record_cursor.int_timestamp
    assert new_state["form1"][Responses.cursor_field] == 100000


def test_get_updated_state_form_id_not_found_in_record():
    # current record doesn't have form_id
    current_state = {"form1": {Responses.cursor_field: 100000}}
    last_record_cursor = pendulum.now(UTC)
    last_record = get_last_record(last_record_cursor, form_id=None)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] == 100000
