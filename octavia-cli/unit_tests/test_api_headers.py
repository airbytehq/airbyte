#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
import uuid
from typing import Dict, Any, List, Tuple

import pytest
import yaml

from octavia_cli.api_headers import deserialize_file_based_headers, ApplicationHeader, deseriliaze_opiton_based_headers, deserialize_api_headers, \
    deduplicate_api_headers, InvalidHeaderConfigurationFile

os.environ["EXAMPLE_ENV_VARIABLE_VALUE"] = "test_header_value"
os.environ["EXAMPLE_ENV_VARIABLE_NAME"] = "test_header_name"

INVALID_FIELDS_YAML_STRING = """
header:
    - name: some_name
      value: some_value
""".strip()

NON_PARSABLE_YAML_FILE = """
some random words
- some dashes:
  - and_next
""".strip()

EMPTY_YAML_FILE = ""


class TestHeadersAssignment:

    @pytest.mark.parametrize(
        "data,expected_count,expected_api_headers", [
            ({
                 "headers": [
                     {"name": "name1", "value": "value1"},
                     {"name": "name2", "value": "value2"},
                     {"name": "name3", "value": "value3"}
                 ]
             },
             3,
             [
                 ApplicationHeader(name="name1", value="value1"),
                 ApplicationHeader(name="name2", value="value2"),
                 ApplicationHeader(name="name3", value="value3")
             ]
            ),
            ({
                 "headers": [
                     {"name": "${EXAMPLE_ENV_VARIABLE_NAME}", "value": "${EXAMPLE_ENV_VARIABLE_VALUE}"},
                 ]
             },
             1,
             [
                 ApplicationHeader(name="test_header_name", value="test_header_value")
             ]
            ),
            ({
                 "headers": [
                     {"name": "name1 ", "value": "value1 "},
                 ]
             },
             1,
             [
                 ApplicationHeader(name="name1", value="value1")
             ]
            ),
            ({
                 "headers": [
                     {"name": "name1", "value": "value1"},
                     {"name": "name1", "value": "value1"},
                     {"name": "name2", "value": "value1"}
                 ]
             },
             2,
             [
                 ApplicationHeader(name="name1", value="value1"),
                 ApplicationHeader(name="name2", value="value1")
             ]
            ),
            ({
                 "headers": [
                     {"name": "name1 ", "value": "value1"},
                     {"name": "name1 ", "value": "value1"},
                     {"name": "name2", "value": "value1"}
                 ]
             },
             2,
             [
                 ApplicationHeader(name="name1", value="value1"),
                 ApplicationHeader(name="name2", value="value1")
             ]
            )
        ]
    )
    def test_read_configuration_yaml_file(self, data: Dict[str, Any], expected_count: int, expected_api_headers: List[ApplicationHeader]):
        # given yaml file
        yaml_file_path = self._produce_yaml_file(data)

        # when loading the configuration file
        api_headers = deserialize_file_based_headers(
            yaml_file_path
        )

        # then headers should match to expected ones

        assert len(api_headers) == expected_count
        assert api_headers == expected_api_headers

        self._remove_temp_yaml_file(yaml_file_path)

    def test_should_not_assign_headers_when_file_is_invalid(self):
        # given not parsable yaml file
        yaml_file_path = self._produce_invalid_yaml_configuration_file(NON_PARSABLE_YAML_FILE)

        # while loading Attribute error should be raised
        with pytest.raises(yaml.scanner.ScannerError):
            deserialize_file_based_headers(yaml_file_path)

        self._remove_temp_yaml_file(yaml_file_path)

    def test_should_raise_an_exception_when_structure_of_file_is_invalid(self):
        # given invalid yaml file data
        yaml_file_path = self._produce_invalid_yaml_configuration_file(INVALID_FIELDS_YAML_STRING)
        empty_yaml_file_path = self._produce_invalid_yaml_configuration_file(EMPTY_YAML_FILE)

        # while loading Attribute error should be raised
        with pytest.raises(AttributeError):
            deserialize_file_based_headers(yaml_file_path)
            deserialize_file_based_headers(empty_yaml_file_path)

        self._remove_temp_yaml_file(yaml_file_path)
        self._remove_temp_yaml_file(empty_yaml_file_path)

    @pytest.mark.parametrize(
        "header_pairs,expected_count,expected_elements",
        [
            (
                    [("name1", "value2"), ("name2", "value4"), ("name3", "value3")],
                    3,
                    [
                        ApplicationHeader(name="name1", value="value2"),
                        ApplicationHeader(name="name2", value="value4"),
                        ApplicationHeader(name="name3", value="value3")
                    ]
            ),
            (
                    [("name1", "value2"), ("name1", "value2"), ("name3", "value3")],
                    2,
                    [
                        ApplicationHeader(name="name1", value="value2"),
                        ApplicationHeader(name="name3", value="value3")
                    ]
            ),
            (
                    [("name2", "value2"), ("name2", "value3")],
                    1,
                    [
                        ApplicationHeader(name="name2", value="value2")
                    ]
            ),
        ]
    )
    def test_should_properly_assign_value_from_arguments_based_approach(self, header_pairs: List[Tuple[str, str]], expected_count: int,
                                                                        expected_elements: List[ApplicationHeader]):
        # when trying to parse header
        parsed_headers = deseriliaze_opiton_based_headers(header_pairs)

        # then count should be as expected
        assert len(parsed_headers) == expected_count

        # and content should also match
        assert parsed_headers == expected_elements

    def test_should_return_api_headers_attributes_when_no_file_provided(self):
        # given api header attributes
        api_header_attributes = [("name", "value1")]

        # when validating api_headers
        parsed_attributes = deserialize_api_headers(api_header_attributes, None)

        # then count should match to expected
        assert len(parsed_attributes) == 1

        # and result configuration should match to expected
        assert parsed_attributes == [ApplicationHeader(name="name", value="value1")]

    def test_should_return_file_based_headers_when_no_attributes_provided(self):
        # given yaml file
        yaml_file_path = self._produce_yaml_file(
            {
                "headers": [
                    {"name": "name1", "value": "value1"}
                ]
            }
        )

        # when validating api headers
        parsed_attributes = deserialize_api_headers(None, yaml_file_path)

        # then result count should be from file based headers
        assert len(parsed_attributes) == 1

        # and content should match
        assert parsed_attributes == [ApplicationHeader(name="name1", value="value1")]

        self._remove_temp_yaml_file(yaml_file_path)

    @pytest.mark.parametrize(
        "file_based_api_headers,argument_based_api_headers,expected_headers",
        [
            (
                    {
                        "headers": [
                            {"name": "name1", "value": "value1"}
                        ]
                    },
                    [],
                    [ApplicationHeader(name="name1", value="value1")]
            ),
            (
                    {
                        "headers": [
                            {"name": "name1", "value": "value1"},
                            {"name": "name2", "value": "value1"},
                        ]
                    },
                    [("name1", "value2"), ("name3", "value4")],
                    [
                        ApplicationHeader(name="name1", value="value2"),
                        ApplicationHeader(name="name2", value="value1"),
                        ApplicationHeader(name="name3", value="value4")
                    ]
            ),
        ]
    )
    def test_should_merge_headers_from_file_and_arguments_when_both_specified(self, file_based_api_headers: Dict[str, Any],
                                                                              argument_based_api_headers: List[Tuple[str, str]],
                                                                              expected_headers: List[ApplicationHeader]):
        # given yaml file with configuration
        yaml_file_path = self._produce_yaml_file(file_based_api_headers)

        # when merging the configuration
        parsed_attributes = deserialize_api_headers(argument_based_api_headers, yaml_file_path)

        # then headers from file should have higher priority
        assert expected_headers == parsed_attributes

        self._remove_temp_yaml_file(yaml_file_path)

    def test_should_raise_exception_when_configuration_file_does_not_exists(self):
        with pytest.raises(FileNotFoundError):
            deserialize_api_headers(None, "/some/path")

    @pytest.mark.parametrize(
        "headers,expected_headers", [
            (
                    [],
                    []
            ),
            (
                    [ApplicationHeader("name1", "value1"), ApplicationHeader("name2", "value2")],
                    [ApplicationHeader("name1", "value1"), ApplicationHeader("name2", "value2")]
            ),
            (
                    [ApplicationHeader("name1", "value1"), ApplicationHeader("name1", "value1"), ApplicationHeader("name2", "value2")],
                    [ApplicationHeader("name1", "value1"), ApplicationHeader("name2", "value2")]
            )
        ]
    )
    def test_deduplicating_headers(self, headers: List[ApplicationHeader], expected_headers: List[ApplicationHeader]):
        # when deduplicating header list
        deduplicated_headers = deduplicate_api_headers(headers)

        # then list should contain unique headers names
        assert expected_headers == deduplicated_headers

    def test_should_raise_invalid_file_exception_when_file_has_invalid_keys(self):
        # given api headers configuration file
        yaml_file_path = self._produce_yaml_file({
            "headers": [
                {"not_name": "name1", "value": "value1"}
            ]
        })

        # when yaml header configuration from file, then exception should be raised

        with pytest.raises(InvalidHeaderConfigurationFile):
            deserialize_file_based_headers(yaml_file_path)

    @staticmethod
    def _produce_yaml_file(data: Dict[str, Any]) -> str:
        random_file_name = f"{uuid.uuid4()}.yaml"

        with open(random_file_name, "w") as file:
            yaml.dump(data, file)
        return random_file_name

    @staticmethod
    def _remove_temp_yaml_file(yaml_file_path: str):
        if os.path.isfile(yaml_file_path):
            os.remove(yaml_file_path)

    def _produce_invalid_yaml_configuration_file(self, data: str):
        random_file_name = f"{uuid.uuid4()}.yaml"

        with open(random_file_name, "w") as file:
            file.write(data)
        return random_file_name
