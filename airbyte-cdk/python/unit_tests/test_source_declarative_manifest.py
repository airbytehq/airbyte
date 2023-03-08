#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from unittest import mock

import pytest
import source_declarative_manifest
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from source_declarative_manifest.main import handle_request

CONFIG = {
    "__injected_declarative_manifest": {
        "version": "0.1.0",
        "definitions": {
            "selector": {"extractor": {"field_path": []}},
            "requester": {"url_base": "https://test.com/api", "http_method": "GET"},
            "retriever": {"record_selector": {"$ref": "#/definitions/selector"}, "requester": {"$ref": "#/definitions/requester"}},
            "base_stream": {"retriever": {"$ref": "#/definitions/retriever"}},
            "data_stream": {"$ref": "#/definitions/base_stream", "$parameters": {"name": "data", "path": "/data"}},
        },
        "streams": [
            "#/definitions/data_stream",
        ],
        "check": {
            "stream_names": [
                "data",
            ]
        },
        "spec": {
            "type": "Spec",
            "documentation_url": "https://test.com/doc",
            "connection_specification": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Test Spec",
                "type": "object",
                "additionalProperties": True,
                "properties": {},
            },
        },
    }
}

CATALOG = {}


@pytest.fixture
def valid_config_file(tmp_path):
    return _write_to_tmp_path(tmp_path, CONFIG, "config")


@pytest.fixture
def catalog_file(tmp_path):
    return _write_to_tmp_path(tmp_path, CATALOG, "catalog")


@pytest.fixture
def config_file_without_injection(tmp_path):
    config = copy.deepcopy(CONFIG)
    del config["__injected_declarative_manifest"]
    return _write_to_tmp_path(tmp_path, config, "config")


@pytest.fixture
def config_file_with_command(tmp_path):
    config = copy.deepcopy(CONFIG)
    config["__command"] = "command"
    return _write_to_tmp_path(tmp_path, config, "config")


def _write_to_tmp_path(tmp_path, config, filename):
    config_file = tmp_path / f"{filename}.json"
    config_file.write_text(json.dumps(config))
    return config_file


def test_on_spec_command_then_raise_value_error(valid_config_file):
    with pytest.raises(ValueError):
        handle_request(["spec", "--config", str(valid_config_file)])


@pytest.mark.parametrize(
    "command",
    [
        pytest.param("check", id="test_check_command_error"),
        pytest.param("discover", id="test_discover_command_error"),
        pytest.param("read", id="test_read_command_error"),
        pytest.param("asdf", id="test_arbitrary_command_error"),
    ],
)
def test_given_no_injected_declarative_manifest_then_raise_value_error(command, config_file_without_injection):
    with pytest.raises(ValueError):
        handle_request([command, "--config", str(config_file_without_injection)])


@pytest.mark.parametrize(
    "command",
    [
        pytest.param("check", id="test_check_command_error"),
        pytest.param("discover", id="test_discover_command_error"),
        pytest.param("read", id="test_read_command_error"),
        pytest.param("asdf", id="test_arbitrary_command_error"),
    ],
)
def test_missing_config_raises_value_error(command):
    with pytest.raises(SystemExit):
        handle_request([command])


@pytest.mark.parametrize(
    "command",
    [
        pytest.param("check", id="test_check_command"),
        pytest.param("discover", id="test_discover_command"),
        pytest.param("read", id="test_read_command"),
    ],
)
def test_given_injected_declarative_manifest_then_launch_with_declarative_manifest(command, valid_config_file, catalog_file):
    with mock.patch("source_declarative_manifest.main.launch") as patch:
        if command == "read":
            handle_request([command, "--config", str(valid_config_file), "--catalog", str(catalog_file)])
        else:
            handle_request([command, "--config", str(valid_config_file)])
        source, _ = patch.call_args[0]
        assert isinstance(source, ManifestDeclarativeSource)


def test_given_injected_declarative_manifest_then_launch_with_declarative_manifest_missing_arg(valid_config_file):
    with pytest.raises(SystemExit):
        handle_request(["read", "--config", str(valid_config_file)])


def test_given_command_then_use_connector_builder_source(config_file_with_command):
    with mock.patch.object(source_declarative_manifest.main.ConnectorBuilderSource, "handle_request") as patch:
        handle_request(["read", "--config", str(config_file_with_command)])
        assert patch.call_count == 1
