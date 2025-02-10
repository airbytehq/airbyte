# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Union

import pytest
import requests
import requests_mock

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class CursorPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token
    Attributes:
        page_size (Optional[int]): the number of records to request
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[InterpolatedBoolean]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
    """

    cursor_value: Union[InterpolatedString, str]
    config: Config
    parameters: Mapping[str, Any]
    page_size: Optional[int] = None
    stop_condition: Optional[Union[InterpolatedBoolean, str]] = None
    decoder: Decoder = field(default_factory=JsonDecoder)

    def __post_init__(self):
        if isinstance(self.cursor_value, str):
            self.cursor_value = InterpolatedString.create(self.cursor_value, parameters=self.parameters)
        if isinstance(self.stop_condition, str):
            self.stop_condition = InterpolatedBoolean(condition=self.stop_condition, parameters=self.parameters)

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        headers = response.headers
        headers["link"] = response.links

        print("STOP CONDITION", self.stop_condition)

        if self.stop_condition:
            should_stop = self.stop_condition.eval(self.config, response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                print("Stopping...")
                return None

        # Update cursor_value with the next_id from the response
        self.cursor_value = InterpolatedString.create(decoded_response.get("next_id"), parameters=self.parameters)
        token = self.cursor_value.eval(config=self.config, last_records=last_records, response=decoded_response, headers=headers)
        print("TOKEN", token)
        return token if token else None

    def reset(self):
        pass

    def get_page_size(self) -> Optional[int]:
        return self.page_size


@pytest.fixture
def mock_responses():
    return ["token_page_init.json", "token_PAY-0L38757939422510JMW5ZJVA.json", "token_PAYID-MW5XXZY5YL87592N34454913.json"]


@pytest.fixture
def cursor_pagination_strategy(mock_responses, stop_condition=None):
    parameters = {}
    decoder = JsonDecoder(parameters=parameters)
    cursor_value = "start_id"  # Initialize with a default value

    for response_file in mock_responses:
        if cursor_value == "start_id":
            cursor_value = load_mock_data(response_file).get("next_id")
        else:
            break  # Stop after getting the next_id from the first response

    return CursorPaginationStrategy(
        cursor_value=cursor_value, config={}, parameters=parameters, page_size=3, stop_condition=stop_condition, decoder=decoder
    )


def load_mock_data(filename):
    with open(os.path.join("./unit_tests/test_files", filename), "r") as file:
        return json.load(file)


def test_cursor_pagination(cursor_pagination_strategy, mock_responses):
    with requests_mock.Mocker() as m:
        base_url = "http://example.com/api/resource"

        # Mock responses
        for i, response_file in enumerate(mock_responses):
            print("")
            print("####################################")
            if i == 0:
                url = f"{base_url}?count=3"
                print("FIRST ITERATION:", response_file, i, url)

            if i > 0:
                url += f"&start_id={next_id}"
                print("NEXT ITERATIONS:", response_file, i, url)
            m.get(url, json=load_mock_data(response_file), status_code=200)
            # Get next_id from the response if it's not the last response

            if i < len(mock_responses) - 1:
                next_id = load_mock_data(response_file)["next_id"]
                print("FOUND NEXT ID:", next_id)

            else:
                next_id = None
                cursor_pagination_strategy(mock_responses, stop_condition=True)

            # Make API call and process response
            response = requests.get(url)
            print("GET RESPONSE:", response)
            assert response.status_code == 200

            decoded_response = response.json()
            last_records = decoded_response["payments"]
            next_id = cursor_pagination_strategy.next_page_token(response, last_records)
            print("NEXT ID:", next_id)

        # Verify the pagination stopped
        assert next_id is None
        print("No more pages")
