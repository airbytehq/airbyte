#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
import responses
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_us_census.source import UsCensusStream


@pytest.fixture
def us_census_stream():
    return UsCensusStream(
        query_params={},
        query_path="data/test",
        api_key="MY_API_KEY",
        authenticator=NoAuth(),
    )


simple_test = '[["name","id"],["A","1"],["B","2"]]'
example_from_docs_test = (
    '[["STNAME","POP","DATE_","state"],'
    '["Alabama","4849377","7","01"],'
    '["Alaska","736732","7","02"],'
    '["Arizona","6731484","7","04"],'
    '["Arkansas","2966369","7","05"],'
    '["California","38802500","7","06"]]'
)


@responses.activate
@pytest.mark.parametrize(
    "response, expected_result",
    [
        (
            simple_test,
            [{"name": "A", "id": "1"}, {"name": "B", "id": "2"}],
        ),
        (
            (
                example_from_docs_test,
                [
                    {
                        "STNAME": "Alabama",
                        "POP": "4849377",
                        "DATE_": "7",
                        "state": "01",
                    },
                    {"STNAME": "Alaska", "POP": "736732", "DATE_": "7", "state": "02"},
                    {
                        "STNAME": "Arizona",
                        "POP": "6731484",
                        "DATE_": "7",
                        "state": "04",
                    },
                    {
                        "STNAME": "Arkansas",
                        "POP": "2966369",
                        "DATE_": "7",
                        "state": "05",
                    },
                    {
                        "STNAME": "California",
                        "POP": "38802500",
                        "DATE_": "7",
                        "state": "06",
                    },
                ],
            )
        ),
        (
            '[["name","id"],["I have an escaped \\" quote","I have an embedded , comma"],["B","2"]]',
            [
                {
                    "name": 'I have an escaped " quote',
                    "id": "I have an embedded , comma",
                },
                {"name": "B", "id": "2"},
            ],
        ),
    ],
)
def test_parse_response(us_census_stream: UsCensusStream, response: str, expected_result: dict):
    responses.add(
        responses.GET,
        us_census_stream.url_base,
        body=response,
    )
    resp = requests.get(us_census_stream.url_base)

    assert list(us_census_stream.parse_response(resp)) == expected_result


type_string = {"type": "string"}


@responses.activate
@pytest.mark.parametrize(
    "response, expected_schema",
    [
        (
            simple_test,
            {
                "name": type_string,
                "id": type_string,
            },
        ),
        (
            example_from_docs_test,
            {
                "STNAME": type_string,
                "POP": type_string,
                "DATE_": type_string,
                "state": type_string,
            },
        ),
    ],
)
def test_discover_schema(us_census_stream: UsCensusStream, response: str, expected_schema: dict):
    responses.add(
        responses.GET,
        f"{us_census_stream.url_base}{us_census_stream.query_path}",
        body=response,
    )
    assert us_census_stream.get_json_schema().get("properties") == expected_schema
