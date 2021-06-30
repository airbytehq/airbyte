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

import json

import pendulum
import vcr
from airbyte_cdk.models import SyncMode
from source_surveymonkey import SourceSurveymonkey


def test_get_updated_state_unit():
    source = SourceSurveymonkey()
    config = json.load(open("secrets/config.json"))
    streams = source.streams(config=config)
    stream = [i for i in streams if i.__class__.__name__ == "Surveys"][0]

    record = {"title": "Market Research - Product Testing Template", "date_modified": "2021-06-08T18:09:00", "id": "306079584"}

    current_state = {"date_modified": "2021-06-10T11:02:01"}
    expected_state = current_state
    assert stream.get_updated_state(current_state, record) == expected_state

    record_with_bigger_date = {"title": "My random title", "date_modified": "2021-06-15T18:09:00", "id": "306079584"}
    expected_state = {stream.cursor_field: record_with_bigger_date[stream.cursor_field]}
    assert stream.get_updated_state(current_state, record_with_bigger_date) == expected_state


def test_get_updated_state():
    source = SourceSurveymonkey()
    config = json.load(open("secrets/config.json"))
    streams = source.streams(config=config)
    surveys_instance = [i for i in streams if i.__class__.__name__ == "Surveys"][0]
    survey_responses_instance = [i for i in streams if i.__class__.__name__ == "SurveyResponses"][0]
    with vcr.use_cassette("pretty_name.yaml", record_mode="new_episodes"):
        surveys_generator = surveys_instance.read_records(sync_mode=SyncMode.full_refresh)
        latest_record = next(surveys_generator)
        survey_id = latest_record["id"]
        survey_responses_generator = survey_responses_instance.read_records(
            sync_mode=SyncMode.full_refresh, stream_slice={"survey_id": survey_id}
        )
        responses_latest_record = next(survey_responses_generator)

    new_state = surveys_instance.get_updated_state(current_stream_state={}, latest_record=latest_record)
    new_response_state = survey_responses_instance.get_updated_state(current_stream_state={}, latest_record=responses_latest_record)
    assert new_state
    assert len(new_state) == 1
    pendulum.parse(list(new_state.values())[0])
    assert new_response_state
    assert survey_id in new_response_state
    expected_date_value = list(new_response_state[survey_id].values())[0]
    pendulum.parse(expected_date_value)
