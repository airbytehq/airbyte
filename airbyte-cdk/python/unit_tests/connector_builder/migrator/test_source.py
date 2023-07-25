#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import pytest
import yaml

from copy import deepcopy

from airbyte_cdk.connector_builder.migrator.source import SourceRepository
from pyfakefs.fake_filesystem_unittest import TestCase

SOURCE_NAME = "source-toto"
A_NO_CODE_MANIFEST = {
    "version": "0.47.1",
    "type": "DeclarativeSource",
    "check": {"type": "CheckStream", "stream_names": ["stream"]},
    "streams": [
        {
            "type": "DeclarativeStream",
            "name": "stream",
            "primary_key": [],
            "schema_loader": {
                "type": "InlineSchemaLoader",
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": True,
                    "properties": {},
                    "type": "object",
                },
            },
            "retriever": {
                "type": "SimpleRetriever",
                "requester": {
                    "type": "HttpRequester",
                    "url_base": "https://a-connector.com",
                    "path": "stream_path",
                    "http_method": "GET",
                    "request_parameters": {},
                    "request_headers": {},
                    "authenticator": {"type": "NoAuth"},
                    "request_body_json": {},
                },
                "record_selector": {
                    "type": "RecordSelector",
                    "extractor": {"type": "DpathExtractor", "field_path": []},
                },
                "paginator": {"type": "NoPagination"},
            },
        }
    ],
}
A_MANIFEST_WITH_CUSTOM_COMPONENT = deepcopy(A_NO_CODE_MANIFEST)
A_MANIFEST_WITH_CUSTOM_COMPONENT["streams"][0]["retriever"] = {
    "type": "CustomRetriever",
    "class_name": "a_custom_package.SampleCustomComponent",
}

A_MANIFEST_WITH_SPEC = deepcopy(A_NO_CODE_MANIFEST)
A_MANIFEST_WITH_SPEC["spec"] = {"any_spec": "spec value"}

A_SPEC = {
    "connectionSpecification": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": [],
        "properties": {},
        "additionalProperties": True
    },
    "documentationUrl": "https://a-documentation-url.com",
    "advanced_auth": {
        "auth_flow_type": "oauth2.0",
        "predicate_key": ["credentials", "auth_type"],
        "predicate_value": "Client",
        "oauth_config_specification": {
            "complete_oauth_server_output_specification": {
                "type": "object",
                "properties": {"refresh_token": {"type": "string"}, "$ref": None},
            }
        },
    }
}


class SourceRepositoryTestCase(TestCase):
    def setUp(self) -> None:
        self.setUpPyfakefs()
        self._repo = SourceRepository(".")

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker) -> None:
        self.mocker = mocker

    def test_given_spec_is_json_when_merge_spec_inside_manifest_then_save_spec_as_part_of_manifest(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST))
        config_path = _config_path_json(SOURCE_NAME)
        self.fs.create_file(config_path, contents=json.dumps(A_SPEC))

        self._repo.merge_spec_inside_manifest(SOURCE_NAME)

        assert not os.path.exists(config_path)
        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["spec"]["connection_specification"] == A_SPEC["connectionSpecification"]
            assert yaml_manifest["spec"]["documentation_url"] == A_SPEC["documentationUrl"]
            assert yaml_manifest["spec"]["advanced_auth"] == A_SPEC["advanced_auth"]

    def test_given_spec_is_yaml_when_merge_spec_inside_manifest_then_save_spec_as_part_of_manifest(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST))
        config_path = _config_path_yaml(SOURCE_NAME)
        self.fs.create_file(config_path, contents=yaml.dump(A_SPEC))

        self._repo.merge_spec_inside_manifest(SOURCE_NAME)

        assert not os.path.exists(config_path)
        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["spec"]["connection_specification"] == A_SPEC["connectionSpecification"]
            assert yaml_manifest["spec"]["documentation_url"] == A_SPEC["documentationUrl"]
            assert yaml_manifest["spec"]["advanced_auth"] == A_SPEC["advanced_auth"]

    def test_given_spec_in_manifest_when_merge_spec_inside_manifest_then_do_not_change_manifest(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_MANIFEST_WITH_SPEC))
        config_path = _config_path_yaml(SOURCE_NAME)
        self.fs.create_file(config_path, contents=yaml.dump(A_SPEC))

        self._repo.merge_spec_inside_manifest(SOURCE_NAME)

        assert not os.path.exists(config_path)
        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["spec"] == A_MANIFEST_WITH_SPEC["spec"]

    def test_when_fetch_no_code_sources_then_return_no_code_source(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST))
        sources = self._repo.fetch_no_code_sources()
        assert sources == [SOURCE_NAME]

    def test_given_source_without_manifest_when_fetch_no_code_sources_then_return_no_code_source(self) -> None:
        self.fs.create_file(f"airbyte-integrations/connectors/{SOURCE_NAME}/source_toto/source.py", contents="some python code")
        sources = self._repo.fetch_no_code_sources()
        assert sources == []

    def test_given_source_has_custom_component_when_fetch_no_code_sources_then_return_no_code_source(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_MANIFEST_WITH_CUSTOM_COMPONENT))
        sources = self._repo.fetch_no_code_sources()
        assert sources == []


def _manifest_path(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/manifest.yaml"


def _config_path_json(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/spec.json"


def _config_path_yaml(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/spec.yaml"
