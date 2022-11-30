#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from source_delighted.source import Bounces, People, SourceDelighted, SurveyResponses, Unsubscribes


@pytest.fixture(scope="module")
def test_config():
    return {
        "api_key": "test_api_key",
        "since": "2022-01-01 00:00:00",
    }


@pytest.fixture(scope="module")
def state():
    return {
        "bounces": {"bounced_at": 1641455286},
        "people": {"created_at": 1641455285},
        "survey_responses": {"updated_at": 1641289816},
        "unsubscribes": {"unsubscribed_at": 1641289584},
    }


BOUNCES_RESPONSE = """
[
    {"person_id": "1046789984", "email": "foo_test204@airbyte.io", "name": "Foo Test204", "bounced_at": 1641455286},
    {"person_id": "1046789989", "email": "foo_test205@airbyte.io", "name": "Foo Test205", "bounced_at": 1641455286}
]
"""


PEOPLE_RESPONSE = """
[
    {"id": "1046789989", "name": "Foo Test205", "email": "foo_test205@airbyte.io", "created_at": 1641455285, "last_sent_at": 1641455285, "last_responded_at": null, "next_survey_scheduled_at": null}
]
"""


SURVEY_RESPONSES_RESPONSE = """
[
    {"id": "210554887", "person": "1042205953", "survey_type": "nps", "score": 0, "comment": "Test Comment202", "permalink": "https://app.delighted.com/r/0q7QEdWzosv5G5c3w9gakivDwEIM5Hq0", "created_at": 1641289816, "updated_at": 1641289816, "person_properties": null, "notes": [], "tags": [], "additional_answers": []},
    {"id": "210554885", "person": "1042205947", "survey_type": "nps", "score": 5, "comment": "Test Comment201", "permalink": "https://app.delighted.com/r/GhWWrBT2wayswOc0AfT7fxpM3UwSpitN", "created_at": 1641289816, "updated_at": 1641289816, "person_properties": null, "notes": [], "tags": [], "additional_answers": []}
]
"""


UNSUBSCRIBES_RESPONSE = """
[
    {"person_id": "1040826319", "email": "foo_test64@airbyte.io", "name": "Foo Test64", "unsubscribed_at": 1641289584}
]
"""


@pytest.mark.parametrize(
    ("stream_class", "url", "response_body"),
    [
        (Bounces, "https://api.delighted.com/v1/bounces.json", BOUNCES_RESPONSE),
        (People, "https://api.delighted.com/v1/people.json", PEOPLE_RESPONSE),
        (SurveyResponses, "https://api.delighted.com/v1/survey_responses.json", SURVEY_RESPONSES_RESPONSE),
        (Unsubscribes, "https://api.delighted.com/v1/unsubscribes.json", UNSUBSCRIBES_RESPONSE),
    ],
)
@responses.activate
def test_not_output_records_where_cursor_field_equals_state(state, test_config, stream_class, url, response_body):
    responses.add(
        responses.GET,
        url,
        body=response_body,
        status=200,
    )

    stream = stream_class(pendulum.parse(test_config["since"]), authenticator=SourceDelighted()._get_authenticator(config=test_config))
    records = [r for r in stream.read_records(SyncMode.incremental, stream_state=state[stream.name])]
    assert not records


def test_example_method():
    assert True
