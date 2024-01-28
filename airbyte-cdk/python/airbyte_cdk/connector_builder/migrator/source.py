#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import shutil
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Tuple

import ruamel.yaml
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow, Spec
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.connector_builder.migrator.schema import SchemaResolver

_NO_CONFIG: Mapping[str, Any] = {}

logger = logging.getLogger("migrator.source")

ManifestModelNode = Dict[str, Any]


class SourceRepository:

    def __init__(self, base_path: str, schema_resolver: Optional[SchemaResolver] = None) -> None:
        self._base_path = os.path.abspath(base_path)
        self._schema_resolver = schema_resolver if schema_resolver is not None else SchemaResolver()

        self._yaml_assembler = ruamel.yaml.YAML()
        self._yaml_assembler.preserve_quotes = True
        self._yaml_assembler.indent(mapping=2, sequence=4, offset=2)
        self._yaml_assembler.width = 4096
        self._yaml_assembler.representer.add_multi_representer(Enum, lambda dumper, enum: dumper.represent_data(enum.value))

    def merge_spec_inside_manifest(self, source_name: str) -> None:
        spec = self._fetch_spec_outside_manifest(source_name)
        if spec:
            manifest_path = self._manifest_path(source_name)
            with open(os.path.join(manifest_path)) as f:
                manifest = self._yaml_assembler.load(f.read())
            if "spec" in manifest:
                # It should be fine to ignore since the CATs test `test_match_expected` ensure that both are the same
                logger.info(
                    f"Source {source_name} has both spec file and spec within manifest. Will keep manifest as-is and delete the spec file"
                )
            else:
                manifest["spec"] = spec.dict(exclude_none=True)

            with open(manifest_path, 'w') as outfile:
                self._yaml_assembler.dump(manifest, outfile)
            self._delete_spec_outside_manifest(source_name)
        else:
            logger.debug(f"Source {source_name} does not have a spec outside the manifest.yaml")

    def _fetch_spec_outside_manifest(self, source_name: str) -> Optional[Spec]:
        json_spec_path, yaml_spec_path = self._get_spec_path(source_name)

        if json_spec_path and os.path.exists(json_spec_path):
            with open(json_spec_path) as json_file:
                return self._assemble_spec(json.load(json_file))
        elif yaml_spec_path and os.path.exists(yaml_spec_path):
            with open(yaml_spec_path) as yaml_file:
                return self._assemble_spec(self._yaml_assembler.load(yaml_file.read()))
        else:
            return None

    @staticmethod
    def _assemble_spec(spec: ManifestModelNode) -> Spec:
        return Spec(
            type="Spec",
            connection_specification=spec["connectionSpecification"],
            documentation_url=spec.get("documentationUrl", None),
            advanced_auth=AuthFlow(**spec["advanced_auth"]) if "advanced_auth" in spec else None
        )

    def _delete_spec_outside_manifest(self, source_name: str) -> None:
        json_spec_path, yaml_spec_path = self._get_spec_path(source_name)

        if json_spec_path and os.path.exists(json_spec_path):
            os.remove(json_spec_path)
        elif yaml_spec_path and os.path.exists(yaml_spec_path):
            os.remove(yaml_spec_path)

    def fetch_no_code_sources(self, skip_list: List[str]) -> List[str]:
        no_code_sources = []

        connectors_folder_path = os.path.join(self._base_path, "airbyte-integrations", "connectors")
        for directory in os.listdir(connectors_folder_path):
            python_package_path = os.path.join(connectors_folder_path, directory, directory.replace("-", "_"))

            if directory in skip_list:
                logger.info(f"skipping {directory}...")
            elif self._is_no_code_connector(python_package_path):
                no_code_sources.append(directory)
        return no_code_sources

    def resolve_no_code_source_path(self, source_name) -> Optional[str]:
        connectors_folder_path = os.path.join(self._base_path, "airbyte-integrations", "connectors")
        python_package_path = os.path.join(connectors_folder_path, source_name, source_name.replace("-", "_"))
        if os.path.exists(python_package_path) and self._is_no_code_connector(python_package_path):
            return python_package_path
        else:
            return None

    @staticmethod
    def _is_no_code_connector(python_package_path: str) -> bool:
        manifest_file_path = os.path.join(python_package_path, "manifest.yaml")
        if not os.path.exists(manifest_file_path):
            return False

        python_source_path = os.path.join(python_package_path, "source.py")
        with open(python_source_path) as python_source_file:
            if "YamlDeclarativeSource" not in python_source_file.read():
                return False

        with open(manifest_file_path) as manifest_file:
            # We can't rely on the `type: Custom*` as some components do not require this tag. We therefore assume that if there is a field
            # `class_name`, it'll be a custom component
            return "class_name:" not in manifest_file.read()

    def _get_spec_path(self, source_name: str) -> Tuple[Optional[str], Optional[str]]:
        json_spec_path = os.path.join(self._python_package_path(source_name), "spec.json")
        yaml_spec_path = os.path.join(self._python_package_path(source_name), "spec.yaml")

        return (
            json_spec_path if os.path.exists(json_spec_path) else None,
            yaml_spec_path if os.path.exists(yaml_spec_path) else None
        )

    def _manifest_path(self, source_name: str) -> str:
        return os.path.join(self._python_package_path(source_name), "manifest.yaml")

    def _schemas_path(self, source_name: str) -> str:
        return os.path.join(self._python_package_path(source_name), "schemas")

    def _python_package_path(self, source_name: str) -> str:
        return os.path.join(self._path_from_name(source_name), source_name.replace("-", "_"))

    def _path_from_name(self, source_name: str) -> str:
        return os.path.join(self._base_path, "airbyte-integrations", "connectors", source_name)

    def delete_schemas_folder(self, source_name: str) -> None:
        schemas_folder_path = os.path.join(self._path_from_name(source_name), source_name.replace("-", "_"), "schemas")
        shutil.rmtree(schemas_folder_path, ignore_errors=True)

    def merge_schemas_inside_manifest(self, source_name: str) -> None:
        python_package_path = self._python_package_path(source_name)
        schemas_path = os.path.join(python_package_path, "schemas")
        if os.path.exists(schemas_path):
            manifest_path = self._manifest_path(source_name)
            with open(manifest_path) as f:
                manifest_model = self._yaml_assembler.load(f.read())

            source = YamlDeclarativeSource(manifest_path)
            for stream in source.streams(_NO_CONFIG):
                if not isinstance(stream, DeclarativeStream):
                    raise ValueError("All streams should be of type DeclarativeStream")
                if isinstance(stream.schema_loader, InlineSchemaLoader):
                    logger.info(f"Stream {stream.name} for {source_name} already has inline schema")
                    continue

                resolved_schema = self._schema_resolver.resolve(python_package_path, stream.name)
                if not resolved_schema:
                    logger.warning(f"Could not find schema in schemas folder for stream {stream.name}")
                    continue

                stream_model = self._fetch_stream_model(manifest_model, stream.name)
                schema_loader_model = self._fetch_or_create_schema_loader_model(stream_model)
                self._clean_json_schema_loaders_even_if_shared(manifest_model, stream_model)
                schema_loader_model.pop("file_path", None)
                schema_loader_model.pop("$parameters", None)
                schema_loader_model["type"] = "InlineSchemaLoader"
                schema_loader_model["schema"] = resolved_schema

            with open(manifest_path, 'w') as outfile:
                self._yaml_assembler.dump(manifest_model, outfile)
        else:
            logger.info(f"Skipping {source_name} as it does not have a schemas folder at {schemas_path}")

    def _clean_json_schema_loaders_even_if_shared(self, manifest_model: ManifestModelNode, stream_model: ManifestModelNode) -> None:
        """
        This method will remove schema loader on all the referenced nodes associated with the stream. Those nodes can be shared accross
        streams so be careful using this method as if you don't intend to delete the node for the other streams, you might break things
        """
        stream_model_ref = stream_model
        while "$ref" in stream_model_ref:
            stream_model_ref = self._extract_ref(manifest_model, stream_model_ref["$ref"])
            if "schema_loader" in stream_model_ref:
                # We assume there if not multiple level of referencing for schema loaders
                if "$ref" in stream_model_ref.get("schema_loader"):  # type: ignore  # MyPy is complaining because stream_model_ref.get("schema_loader") is typed as Any but in practice, it is a Dict[str, any]
                    self._delete_ref(manifest_model, stream_model_ref["schema_loader"]["$ref"])
                    stream_model_ref.pop("schema_loader", None)
                stream_model_ref.pop("schema_loader", None)

        if "$ref" in stream_model.get("schema_loader", {}):
            self._delete_ref(manifest_model, stream_model["schema_loader"]["$ref"])
            stream_model["schema_loader"].pop("$ref", None)

    def _fetch_or_create_schema_loader_model(self, stream_model: ManifestModelNode) -> ManifestModelNode:
        if "schema_loader" not in stream_model:
            schema_loader: Dict[Any, Any] = {}
            stream_model["schema_loader"] = schema_loader
            return schema_loader
        else:
            return stream_model["schema_loader"]  # type: ignore  # in practice, this is ManifestModelNode

    def _fetch_stream_model(self, manifest_model: ManifestModelNode, stream_name: str) -> ManifestModelNode:
        for manifest_stream in manifest_model["streams"]:
            manifest_stream_model = (
                self._extract_ref(manifest_model, manifest_stream)
                if isinstance(manifest_stream, str)
                else manifest_stream
            )
            name = (
                manifest_stream_model.get("name", "")
                if "name" in manifest_stream_model
                else manifest_stream_model.get("$parameters", {}).get("name", "")
            )

            if not name:
                raise ValueError(f"No name found for stream {manifest_stream}")
            if name == stream_name:
                return manifest_stream_model  # type: ignore  # in practice, this is ManifestModelNode
        raise ValueError(f"Could not find stream {stream_name} in manifest")

    def _extract_ref(self, manifest_model: ManifestModelNode, ref: str) -> ManifestModelNode:
        return self._get_nested_value(manifest_model, self._tokenize_ref(ref))

    def _delete_ref(self, manifest_model: ManifestModelNode, ref: str) -> None:
        ref_path = self._tokenize_ref(ref)
        result = manifest_model
        for k in ref_path[:-1]:
            result = result[k]
        result.pop(ref_path[-1], None)

    def _tokenize_ref(self, ref: str) -> List[str]:
        return ref.replace("#/", "").split("/")

    @staticmethod
    def _get_nested_value(dictionary: ManifestModelNode, keys: List[str]) -> ManifestModelNode:
        result = dictionary
        for k in keys:
            result = result[k]
        return result
