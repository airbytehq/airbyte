#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json

import pytest
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from source_declarative_manifest.run import create_manifest, handle_command

CONFIG = {
    "__injected_declarative_manifest": {
        "version": "0.29.0",
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
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(CONFIG))
    return config_file


@pytest.fixture
def config_file_without_injection(tmp_path):
    config = copy.deepcopy(CONFIG)
    del config["__injected_declarative_manifest"]

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return config_file


def test_spec_does_not_raise_value_error():
    handle_command(["spec"])


def test_given_no_injected_declarative_manifest_then_raise_value_error(config_file_without_injection):
    with pytest.raises(ValueError):
        create_manifest(["check", "--config", str(config_file_without_injection)])


def test_given_injected_declarative_manifest_then_return_declarative_manifest(valid_config_file):
    source = create_manifest(["check", "--config", str(valid_config_file)])
    assert isinstance(source, ManifestDeclarativeSource)
