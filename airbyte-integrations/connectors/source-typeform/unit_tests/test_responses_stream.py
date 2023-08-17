#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Optional

import pendulum
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from pendulum.datetime import DateTime
from source_typeform.source import Responses

start_date_str = "2020-06-27T15:32:38Z"
start_date = pendulum.parse(start_date_str)
start_date_ts = start_date.int_timestamp
config = {"token": "10", "start_date": start_date_str, "page_size": 2}

UTC = pendulum.timezone("UTC")
responses = Responses(authenticator=TokenAuthenticator(token=config["token"]), **config)


def get_last_record(last_record_cursor: DateTime, form_id: Optional[str] = "form1") -> Mapping[str, Any]:
    metadata = {"referer": f"http://134/{form_id}"} if form_id else {}
    return {Responses.cursor_field: last_record_cursor.format(Responses.date_format), "metadata": metadata}


def test_get_updated_state_new():
    # current record cursor greater than current state
    current_state = {"form1": {Responses.cursor_field: start_date_ts + 100000}}
    last_record_cursor = pendulum.now(UTC)
    last_record = get_last_record(last_record_cursor)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] == last_record_cursor.format(Responses.date_format)


def test_get_updated_state_not_changed():
    # current record cursor less than current state
    current_state = {"form1": {Responses.cursor_field: start_date_ts + 100000}}
    last_record_cursor = pendulum.from_timestamp(start_date_ts + 100)
    last_record = get_last_record(last_record_cursor)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] == pendulum.from_timestamp(start_date_ts + 100000).format(Responses.date_format)


def test_get_updated_state_form_id_is_new():
    # current record has new form id which is not exists in current state
    current_state = {"form1": {Responses.cursor_field: start_date_ts + 100000}}
    last_record_cursor = pendulum.from_timestamp(start_date_ts + 100)
    last_record = get_last_record(last_record_cursor, form_id="form2")

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form2"][Responses.cursor_field] == last_record_cursor.format(Responses.date_format)
    assert new_state["form1"][Responses.cursor_field] == start_date_ts + 100000


def test_get_updated_state_form_id_not_found_in_record():
    # current record doesn't have form_id
    current_state = {"form1": {Responses.cursor_field: 100000}}
    last_record_cursor = pendulum.now(UTC)
    last_record = get_last_record(last_record_cursor, form_id=None)

    new_state = responses.get_updated_state(current_state, last_record)
    assert new_state["form1"][Responses.cursor_field] == 100000
