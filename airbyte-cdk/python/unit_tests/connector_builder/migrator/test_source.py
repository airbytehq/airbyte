#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from copy import deepcopy
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
import yaml
from airbyte_cdk.connector_builder.migrator.schema import SchemaResolver
from airbyte_cdk.connector_builder.migrator.source import SourceRepository
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from pyfakefs.fake_filesystem_unittest import TestCase
from pytest_mock.plugin import MockerFixture
from unit_tests.unit_test_tooling.manifest import ManifestBuilder, ManifestStreamBuilder

SOURCE_NAME = "source-toto"
STREAM_NAME = "stream-name"
ANOTHER_STREAM_NAME = "another-stream-name"
SCHEMA_REF = "schema_ref"
A_NO_CODE_MANIFEST_WITHOUT_SPEC = ManifestBuilder().without_spec().build()
A_MANIFEST_WITH_CUSTOM_COMPONENT: Dict[str, Any] = deepcopy(A_NO_CODE_MANIFEST_WITHOUT_SPEC)
A_MANIFEST_WITH_CUSTOM_COMPONENT["streams"][0]["retriever"] = {
    "type": "CustomRetriever",
    "class_name": "a_custom_package.SampleCustomComponent",
}

A_SCHEMA = {
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    }
  },
  "$schema": "http://json-schema.org/schema#"
}

ANOTHER_SCHEMA = {
  "type": "object",
  "properties": {
    "another_id": {
      "type": "string"
    }
  },
  "$schema": "http://json-schema.org/schema#"
}


A_MANIFEST_WITH_SPEC = deepcopy(A_NO_CODE_MANIFEST_WITHOUT_SPEC)
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

PYTHON_SOURCE_CONTENT = """
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
class SourceToto(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
"""


class SourceRepositoryTestCase(TestCase):
    def setUp(self) -> None:
        self.setUpPyfakefs()
        self._schema_resolver = Mock(spec=SchemaResolver)
        self._repo = SourceRepository(".", self._schema_resolver)

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture) -> None:
        self.mocker = mocker

    def test_given_spec_is_json_when_merge_spec_inside_manifest_then_save_spec_as_part_of_manifest(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST_WITHOUT_SPEC))
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
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST_WITHOUT_SPEC))
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

    def test_when_fetch_no_code_sources_then_return_source_is_not_code(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST_WITHOUT_SPEC))
        self.fs.create_file(_python_source_path(SOURCE_NAME), contents=PYTHON_SOURCE_CONTENT)

        sources = self._repo.fetch_no_code_sources()

        assert sources == [SOURCE_NAME]

    def test_given_source_without_manifest_when_fetch_no_code_sources_then_return_empty_list(self) -> None:
        self.fs.create_file(f"airbyte-integrations/connectors/{SOURCE_NAME}/source_toto/source.py", contents="some python code")
        sources = self._repo.fetch_no_code_sources()
        assert sources == []

    def test_given_source_has_custom_component_when_fetch_no_code_sources_then_return_empty_list(self) -> None:
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_MANIFEST_WITH_CUSTOM_COMPONENT))
        self.fs.create_file(_python_source_path(SOURCE_NAME), contents=PYTHON_SOURCE_CONTENT)

        sources = self._repo.fetch_no_code_sources()

        assert sources == []

    def test_given_python_code_does_not_import_yaml_declarative_when_fetch_no_code_sources_then_return_empty_list(self):
        self.fs.create_file(_manifest_path(SOURCE_NAME), contents=yaml.dump(A_NO_CODE_MANIFEST_WITHOUT_SPEC))
        self.fs.create_file(_python_source_path(SOURCE_NAME), contents="class SourceSendgrid(AbstractSource):\n    pass")

        sources = self._repo.fetch_no_code_sources()

        assert sources == []

    def test_given_schemas_folder_with_files_when_delete_schemas_then_delete(self) -> None:
        schemas_path = _schemas_path(SOURCE_NAME)
        self.fs.create_file(os.path.join(schemas_path, "a-file.json"), contents='{"any_schema": 1}')
        self.fs.create_file(os.path.join(schemas_path, "another-file.json"), contents='{"any_schema": 1}')

        self._repo.delete_schemas_folder(SOURCE_NAME)

        assert not os.path.exists(schemas_path)

    def test_given_schemas_folder_with_folders_when_delete_schemas_then_delete(self) -> None:
        schemas_path = _schemas_path(SOURCE_NAME)
        self.fs.create_file(os.path.join(schemas_path, "a-folder", "a-file.json"))

        self._repo.delete_schemas_folder(SOURCE_NAME)

        assert not os.path.exists(schemas_path)

    def test_given_no_schemas_folder_when_delete_schemas_then_do_nothing(self) -> None:
        self._repo.delete_schemas_folder(SOURCE_NAME)
        # if it does raise an exception here, we're happy

    @patch("airbyte_cdk.connector_builder.migrator.source.YamlDeclarativeSource")
    def test_given_stream_by_reference_when_merge_schemas_inside_manifest_then_merge_schema_in_referenced_stream(self, source_patch) -> None:
        self._given_streams_from_yaml_declarative_source(source_patch)
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, STREAM_NAME)
        self._given_manifest_yaml_file(
            SOURCE_NAME,
            ManifestBuilder().with_stream(ManifestStreamBuilder().with_name(STREAM_NAME).with_schema(inline=False), by_ref=STREAM_NAME).build()
        )

        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)

        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["definitions"][STREAM_NAME]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": A_SCHEMA,
            }

    @patch("airbyte_cdk.connector_builder.migrator.source.YamlDeclarativeSource")
    def test_given_schema_loader_by_reference_when_merge_schemas_inside_manifest_then_merge_schema_in_referenced_schema_loader(self, source_patch) -> None:
        self._given_streams_from_yaml_declarative_source(source_patch)
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, STREAM_NAME)
        self._given_manifest_yaml_file(
            SOURCE_NAME,
            ManifestBuilder().with_stream(ManifestStreamBuilder().with_name(STREAM_NAME).with_schema(inline=False, by_ref=SCHEMA_REF)).build()
        )

        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)

        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["definitions"] == {}
            assert yaml_manifest["streams"][0]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": A_SCHEMA,
            }

    @patch("airbyte_cdk.connector_builder.migrator.source.YamlDeclarativeSource")
    def test_given_schema_loader_not_by_reference_when_merge_schemas_inside_manifest_then_merge_schema_in_stream_schema_loader(self, source_patch) -> None:
        self._given_streams_from_yaml_declarative_source(source_patch)
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, STREAM_NAME)
        self._given_manifest_yaml_file(
            SOURCE_NAME,
            ManifestBuilder().with_stream(ManifestStreamBuilder().with_name(STREAM_NAME).with_schema(inline=False)).build()
        )

        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)

        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["streams"][0]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": A_SCHEMA,
            }

    @patch("airbyte_cdk.connector_builder.migrator.source.YamlDeclarativeSource")
    def test_given_json_schema_loader_in_referenced_stream_when_merge_schemas_inside_manifest_then_remove_schema_loader(self, source_patch) -> None:
        self._given_streams_from_yaml_declarative_source(source_patch)
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, STREAM_NAME)
        self._given_manifest_yaml_file(
            SOURCE_NAME,
            {
                "version": "0.47.0",
                "type": "DeclarativeSource",
                "check": {
                    "type": "CheckStream",
                    "stream_names": [STREAM_NAME]
                },
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "$ref": "#/definitions/base_stream",
                        "name": STREAM_NAME,
                        "primary_key": [],
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://an-api.com",
                                "path": "/a-path/",
                                "http_method": "GET",
                            },
                            "record_selector": {
                                "type": "RecordSelector",
                                "extractor": {
                                    "type": "DpathExtractor",
                                    "field_path": []
                                }
                            },
                        }
                    }
                ],
                "definitions": {
                    "base_stream": {
                        "schema_loader": {
                            "type": "JsonFileSchemaLoader",
                            "file_path": "./source_toto/schemas/schema-name.json",
                        }
                    }
                }
            }
        )

        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)

        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert yaml_manifest["definitions"]["base_stream"] == {}
            assert yaml_manifest["streams"][0]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": A_SCHEMA,
            }

    @patch("airbyte_cdk.connector_builder.migrator.source.YamlDeclarativeSource")
    def test_given_two_streams_referencing_same_schema_loader_when_merge_schemas_inside_manifest_then_remove_schema_loader(self, source_patch) -> None:
        self._given_streams_from_yaml_declarative_source(source_patch, [STREAM_NAME, ANOTHER_STREAM_NAME])
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, STREAM_NAME)
        self._given_schema_file_for_stream(A_SCHEMA, SOURCE_NAME, ANOTHER_STREAM_NAME)
        self._schema_resolver.resolve.side_effect = [A_SCHEMA, ANOTHER_SCHEMA]
        self._given_manifest_yaml_file(
            SOURCE_NAME,
            {
                "version": "0.47.0",
                "type": "DeclarativeSource",
                "check": {
                    "type": "CheckStream",
                    "stream_names": [STREAM_NAME, ANOTHER_STREAM_NAME]
                },
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "schema_loader": {"$ref": "#/definitions/schema_loader"},
                        "name": STREAM_NAME,
                        "primary_key": [],
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://an-api.com",
                                "path": "/a-path/",
                                "http_method": "GET",
                            },
                            "record_selector": {
                                "type": "RecordSelector",
                                "extractor": {
                                    "type": "DpathExtractor",
                                    "field_path": []
                                }
                            },
                        }
                    },
                    {
                        "type": "DeclarativeStream",
                        "schema_loader": {"$ref": "#/definitions/schema_loader"},
                        "name": ANOTHER_STREAM_NAME,
                        "primary_key": [],
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://an-api.com",
                                "path": "/a-path/",
                                "http_method": "GET",
                            },
                            "record_selector": {
                                "type": "RecordSelector",
                                "extractor": {
                                    "type": "DpathExtractor",
                                    "field_path": []
                                }
                            },
                        }
                    }
                ],
                "definitions": {
                    "schema_loader": {
                        "type": "JsonFileSchemaLoader",
                        "file_path": "./source_toto/schemas/{{ parameters.name }}.json",
                    }
                }
            }
        )

        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)

        with open(_manifest_path(SOURCE_NAME), "r") as manifest_file:
            yaml_manifest = yaml.safe_load(manifest_file)
            assert "schema_loader" not in yaml_manifest["definitions"]
            assert yaml_manifest["streams"][0]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": A_SCHEMA,
            }
            assert yaml_manifest["streams"][1]["schema_loader"] == {
                "type": "InlineSchemaLoader",
                "schema": ANOTHER_SCHEMA,
            }

    def test_given_no_schemas_folder_when_merge_schemas_inside_manifest_then_do_nothing(self) -> None:
        self._repo.merge_schemas_inside_manifest(SOURCE_NAME)
        assert self._schema_resolver.resolve.call_count == 0

    def _given_manifest_yaml_file(self, source_name: str, manifest_model) -> None:
        self.fs.create_file(_manifest_path(source_name), contents=yaml.dump(manifest_model))

    def _given_schema_file_for_stream(self, schema, source_name: str, stream_name: str) -> None:
        # The content of the file is not important as the SchemaResolver will take care of that. We only create the folder because the
        # SourceRepository will skip the sources where the `schemas` folder does not exist
        self.fs.create_file(
            os.path.join(_schemas_path(source_name), f"{stream_name}.json"),
            contents=f"schema file for stream {stream_name}"
        )
        self._schema_resolver.resolve.return_value = schema

    def _given_streams_from_yaml_declarative_source(self, source_patch, stream_names=[]) -> None:
        if stream_names:
            source_patch.return_value.streams.return_value = [self._a_stream(name) for name in stream_names]
        else:
            source_patch.return_value.streams.return_value = [self._a_stream(STREAM_NAME)]

    def _a_stream(self, stream_name: str) -> DeclarativeStream:
        stream = Mock(spec=DeclarativeStream)
        stream.name = stream_name
        return stream


def _schemas_path(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/schemas"


def _manifest_path(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/manifest.yaml"


def _python_source_path(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/source.py"


def _config_path_json(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/spec.json"


def _config_path_yaml(source_name: str) -> str:
    return f"airbyte-integrations/connectors/{source_name}/{source_name.replace('-', '_')}/spec.yaml"
