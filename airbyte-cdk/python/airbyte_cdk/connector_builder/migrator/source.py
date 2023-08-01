#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import ruamel.yaml
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow, Spec

logger = logging.getLogger("migrator.source")


class SourceRepository:

    def __init__(self, base_path: str) -> None:
        self._base_path = base_path

    def merge_spec_inside_manifest(self, source_name: str) -> None:
        spec = self._fetch_spec_outside_manifest(source_name)
        if spec:
            manifest_path = self._manifest_path(source_name)
            yaml = ruamel.yaml.YAML()
            yaml.preserve_quotes = True
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.width = 4096
            yaml.representer.add_multi_representer(Enum, lambda dumper, enum: dumper.represent_data(enum.value))
            with open(os.path.join(manifest_path)) as f:
                manifest = yaml.load(f.read())
            if "spec" in manifest:
                # It should be fine to ignore since the CATs test `test_match_expected` ensure that both are the same
                logger.info(
                    f"Source {source_name} has both spec file and spec within manifest. Will keep manifest as-is and delete the spec file"
                )
            else:
                manifest["spec"] = spec.dict(exclude_none=True)

            with open(manifest_path, 'w') as outfile:
                yaml.dump(manifest, outfile)
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
                yaml = ruamel.yaml.YAML()
                return self._assemble_spec(yaml.load(yaml_file.read()))
        else:
            return None

    @staticmethod
    def _assemble_spec(spec: Dict[str, Any]) -> Spec:
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

    def fetch_no_code_sources(self) -> List[str]:
        no_code_sources = []

        connectors_folder_path = os.path.join("airbyte-integrations", "connectors")
        for directory in os.listdir(connectors_folder_path):
            manifest_file_path = os.path.join(connectors_folder_path, directory, directory.replace("-", "_"), "manifest.yaml")
            if self._is_no_code_connector(manifest_file_path):
                no_code_sources.append(directory)
        return no_code_sources

    @staticmethod
    def _is_no_code_connector(manifest_file_path: str) -> bool:
        if not os.path.exists(manifest_file_path):
            return False

        with open(manifest_file_path) as manifest_file:
            file_content = manifest_file.read()
            # We can't rely on the `type: Custom*` as some components do not require this tag. We therefore assume that if there is a field
            # `class_name`, it'll be a custom component
            return not re.search("class_name:", file_content)

    def _get_spec_path(self, source_name: str) -> Tuple[Optional[str], Optional[str]]:
        json_spec_path = os.path.join(self._python_package_path(source_name), "spec.json")
        yaml_spec_path = os.path.join(self._python_package_path(source_name), "spec.yaml")

        return (
            json_spec_path if os.path.exists(json_spec_path) else None,
            yaml_spec_path if os.path.exists(yaml_spec_path) else None
        )

    def _manifest_path(self, source_name: str) -> str:
        return os.path.join(self._python_package_path(source_name), "manifest.yaml")

    def _python_package_path(self, source_name: str) -> str:
        return os.path.join(self._path_from_name(source_name), source_name.replace("-", "_"))

    def _path_from_name(self, source_name: str) -> str:
        return os.path.join(self._base_path, "airbyte-integrations", "connectors", source_name)
