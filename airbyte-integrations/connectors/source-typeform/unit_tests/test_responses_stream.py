#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
