#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock

import pendulum
import pytest
import requests
from pydantic import BaseModel
from source_klaviyo.streams import IncrementalKlaviyoStreamLatest, Profiles

START_DATE = pendulum.datetime(2020, 10, 10)


class SomeIncrementalStream(IncrementalKlaviyoStreamLatest):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "sub_path"


@pytest.fixture(name="response")
def response_fixture(mocker):
    return mocker.Mock(spec=requests.Response)


class TestIncrementalKlaviyoStreamLatest:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class IncrementalKlaviyoStreamLatest with abstract methods cursor_field, path"
        ):
            IncrementalKlaviyoStreamLatest(api_key="some_key", start_date=START_DATE.isoformat())

    @pytest.mark.parametrize(
        ["response_json", "next_page_token"],
        [
            (
              {
                "data": [
                    {"type": "profile", "id": "00AA0A0AA0AA000AAAAAAA0AA0"},
                ],
                "links": {
                  "self": "https://a.klaviyo.com/api/profiles/",
                  "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                  "prev": "null"
                }
              },
              {
                "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"
              }
            )
        ],
    )
    def test_next_page_token(self, response, response_json, next_page_token):
        response.json.return_value = response_json
        stream = SomeIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.next_page_token(response)

        assert result == next_page_token


class TestProfilesStream:
    def test_parse_response(self, mocker):
        stream = Profiles(api_key="some_key", start_date=START_DATE.isoformat())
        json = {
            "data": [
                {
                  "type": "profile",
                  "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                  "attributes": {
                    "email": "name@airbyte.io",
                    "phone_number": "+11111111111",
                    "updated": "2023-03-10T20:36:36+00:00"
                  },
                  "properties": {
                    "Status": "onboarding_complete"
                  }
                },
                {
                  "type": "profile",
                  "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                  "attributes": {
                    "email": "name2@airbyte.io",
                    "phone_number": "+2222222222",
                    "updated": "2023-02-10T20:36:36+00:00"
                  },
                  "properties": {
                    "Status": "onboarding_started"
                  }
                }
            ],
            "links": {
              "self": "https://a.klaviyo.com/api/profiles/",
              "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
              "prev": "null"
            }
        }
        records = list(stream.parse_response(mocker.Mock(json=mocker.Mock(return_value=json))))
        assert records == [
            {
              "type": "profile",
              "id": "00AA0A0AA0AA000AAAAAAA0AA0",
              "updated": "2023-03-10T20:36:36+00:00",
              "attributes": {
                "email": "name@airbyte.io",
                "phone_number": "+11111111111",
                "updated": "2023-03-10T20:36:36+00:00"
              },
              "properties": {
                "Status": "onboarding_complete"
              }
            },
            {
              "type": "profile",
              "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
              "updated": "2023-02-10T20:36:36+00:00",
              "attributes": {
                "email": "name2@airbyte.io",
                "phone_number": "+2222222222",
                "updated": "2023-02-10T20:36:36+00:00"
              },
              "properties": {
                "Status": "onboarding_started"
              }
            }
        ]
