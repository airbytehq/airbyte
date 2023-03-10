#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from typing import Mapping, Any
from unittest import mock

import pytest

import source_declarative_manifest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from source_declarative_manifest.main import handle_connector_builder_request, handle_request
from unit_tests.connector_builder.utils import create_configured_catalog_dict

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


@pytest.fixture
def valid_config_file(tmp_path):
    return _write_to_tmp_path(tmp_path, CONFIG, "config")


@pytest.fixture
def catalog_file(tmp_path):
    return _write_to_tmp_path(tmp_path, create_configured_catalog_dict("my_stream"), "catalog")


@pytest.fixture
def config_file_without_injection(tmp_path):
    config = copy.deepcopy(CONFIG)
    del config["__injected_declarative_manifest"]
    return _write_to_tmp_path(tmp_path, config, "config")


@pytest.fixture
def config_file_with_command(tmp_path):
    config = copy.deepcopy(CONFIG)
    config["__test_read_config"] = {"max_records": 10}
    return _write_to_tmp_path(tmp_path, config, "config")


def _write_to_tmp_path(tmp_path, config, filename):
    config_file = tmp_path / f"{filename}.json"
    config_file.write_text(json.dumps(config))
    return config_file


def test_on_spec_command_then_raise_value_error(valid_config_file):
    with pytest.raises(SystemExit):
        handle_request(["spec", "--config", str(valid_config_file)])


@pytest.mark.parametrize(
    "command, expected_exception_type",
    [
        pytest.param("check", ValueError, id="test_check_command_error"),
        pytest.param("discover", ValueError, id="test_discover_command_error"),
        pytest.param("read", ValueError, id="test_read_command_error"),
        pytest.param("asdf", SystemExit, id="test_arbitrary_command_error")
    ],
)
def test_given_no_injected_declarative_manifest_then_raise_error(command, expected_exception_type, config_file_without_injection, catalog_file):
    with pytest.raises(expected_exception_type):
        if command == "read":
            handle_request([command, "--config", str(config_file_without_injection), "--catalog", str(catalog_file)])
        else:
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


def test_given_command_then_use_connector_builder_handler(config_file_with_command, catalog_file):
    with mock.patch.object(source_declarative_manifest.main, "handle_connector_builder_request") as patch:
        handle_request(["read", "--config", str(config_file_with_command), "--catalog", str(catalog_file)])
        assert patch.call_count == 1


@pytest.mark.parametrize(
    "command",
    [
        pytest.param("asdf", id="test_arbitrary_command_error"),
        pytest.param(None, id="test_command_is_none_error"),
        pytest.param("", id="test_command_is_empty_error"),
    ],
)
def test_invalid_command(command):
    config = copy.deepcopy(CONFIG)
    source = ManifestDeclarativeSource(CONFIG["__injected_declarative_manifest"])
    with pytest.raises(Exception):
        handle_connector_builder_request(source, config, ConfiguredAirbyteCatalog.parse_obj(create_configured_catalog_dict(command)))

