#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

import pytest
from jsonschema import ValidationError
from source_declarative_manifest import run

POKEAPI_JSON_SPEC_SUBSTRING = '"required":["pokemon_name"]'
SUCCESS_CHECK_SUBSTRING = '"connectionStatus":{"status":"SUCCEEDED"}'
FAILED_CHECK_SUBSTRING = '"connectionStatus":{"status":"FAILED"}'


@pytest.fixture(autouse=True)
def setup(valid_local_manifest_yaml):
    with patch('source_declarative_manifest.run._is_local_manifest_command', return_value=True):
        with patch('source_declarative_manifest.run.YamlDeclarativeSource._read_and_parse_yaml_file', return_value=valid_local_manifest_yaml):
            yield


def test_spec_is_poke_api(capsys):
    run.handle_command(["spec"])
    stdout = capsys.readouterr()
    assert POKEAPI_JSON_SPEC_SUBSTRING in stdout.out


def test_invalid_yaml_throws(capsys, invalid_local_manifest_yaml):
        with patch('source_declarative_manifest.run.YamlDeclarativeSource._read_and_parse_yaml_file', return_value=invalid_local_manifest_yaml):
            with pytest.raises(ValidationError):
                run.handle_command(["spec"])


def test_given_invalid_config_then_unsuccessful_check(capsys, invalid_local_config_file):
    run.handle_command(["check", "--config", str(invalid_local_config_file)])
    stdout = capsys.readouterr()
    assert json.loads(stdout.out).get("connectionStatus").get("status") == "FAILED"


def test_given_valid_config_with_successful_check(capsys, valid_local_config_file):
    run.handle_command(["check", "--config", str(valid_local_config_file)])
    stdout = capsys.readouterr()
    assert SUCCESS_CHECK_SUBSTRING in stdout.out
