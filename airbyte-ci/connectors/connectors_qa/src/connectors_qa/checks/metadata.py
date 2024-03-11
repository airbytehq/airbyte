# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import os

import toml
from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult
from metadata_service.validators.metadata_validator import PRE_UPLOAD_VALIDATORS, ValidatorOptions, validate_and_load  # type: ignore


class MetadataCheck(Check):
    category = CheckCategory.METADATA


class ValidateMetadata(MetadataCheck):
    name = f"Connectors must have valid {consts.METADATA_FILE_NAME} file"
    description = f"Connectors must have a `{consts.METADATA_FILE_NAME}` file at the root of their directory. This file is used to build our connector registry. Its structure must follow our metadata schema. Field values are also validated. This is to ensure that all connectors have the required metadata fields and that the metadata is valid. More details in this [documentation]({consts.METADATA_DOCUMENTATION_URL})."
    # Metadata lib required the following env var to be set
    # to check if the base image is on DockerHub
    required_env_vars = {
        consts.DOCKER_HUB_USERNAME_ENV_VAR_NAME,
        consts.DOCKER_HUB_PASSWORD_ENV_VAR_NAME,
    }

    def __init__(self) -> None:
        for env_var in self.required_env_vars:
            if env_var not in os.environ:
                raise ValueError(f"Environment variable {env_var} is required for this check")
        super().__init__()

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="User facing documentation file is missing. Please create it",
            )
        deserialized_metadata, error = validate_and_load(
            connector.metadata_file_path,
            PRE_UPLOAD_VALIDATORS,
            ValidatorOptions(docs_path=str(connector.documentation_file_path)),
        )
        if not deserialized_metadata:
            return self.fail(connector=connector, message=f"Metadata file is invalid: {error}")

        return self.pass_(
            connector=connector,
            message="Metadata file valid.",
        )


class CheckConnectorLanguageTag(MetadataCheck):
    name = "Connector must have a language tag in metadata"
    description = f"Connectors must have a language tag in their metadata. It must be set in the `tags` field in {consts.METADATA_FILE_NAME}. The values can be `language:python` or `language:java`. This checks infers the correct language tag based on the presence of certain files in the connector directory."

    PYTHON_LANGUAGE_TAG = "language:python"
    JAVA_LANGUAGE_TAG = "language:java"

    def get_expected_language_tag(self, connector: Connector) -> str:
        if (connector.code_directory / consts.SETUP_PY_FILE_NAME).exists() or (
            connector.code_directory / consts.PYPROJECT_FILE_NAME
        ).exists():
            return self.PYTHON_LANGUAGE_TAG
        elif (connector.code_directory / consts.GRADLE_FILE_NAME).exists():
            return self.JAVA_LANGUAGE_TAG
        else:
            raise ValueError("Could not infer the language tag from the connector directory")

    def _run(self, connector: Connector) -> CheckResult:
        try:
            expected_language_tag = self.get_expected_language_tag(connector)
        except ValueError:
            return self.fail(
                connector=connector,
                message="Could not infer the language tag from the connector directory",
            )

        current_language_tags = [t for t in connector.metadata.get("tags", []) if t.startswith("language:")]
        if not current_language_tags:
            return self.fail(
                connector=connector,
                message="Language tag is missing in the metadata file",
            )
        if len(current_language_tags) > 1:
            return self.fail(
                connector=connector,
                message=f"Multiple language tags found in the metadata file: {current_language_tags}",
            )
        current_language_tag = current_language_tags[0]
        if current_language_tag != expected_language_tag:
            return self.fail(
                connector=connector,
                message=f"Expected language tag '{expected_language_tag}' in the {consts.METADATA_FILE_NAME} file, but found '{current_language_tag}'",
            )
        return self.pass_(
            connector=connector,
            message=f"Language tag {expected_language_tag} is present in the metadata file",
        )


class CheckConnectorCDKTag(MetadataCheck):
    name = "Python connectors must have a CDK tag in metadata"
    description = f"Python connectors must have a CDK tag in their metadata. It must be set in the `tags` field in {consts.METADATA_FILE_NAME}. The values can be `cdk:low-code`, `cdk:python`, or `cdk:file`."
    applies_to_connector_languages = [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]

    class CDKTag:
        LOW_CODE = "cdk:low-code"
        PYTHON = "cdk:python"
        FILE = "cdk:python-file-based"

    def get_expected_cdk_tag(self, connector: Connector) -> str:
        manifest_file = connector.code_directory / connector.technical_name.replace("-", "_") / consts.LOW_CODE_MANIFEST_FILE_NAME
        pyproject_file = connector.code_directory / consts.PYPROJECT_FILE_NAME
        setup_py_file = connector.code_directory / consts.SETUP_PY_FILE_NAME
        if manifest_file.exists():
            return self.CDKTag.LOW_CODE
        if pyproject_file.exists():
            pyproject = toml.load((connector.code_directory / consts.PYPROJECT_FILE_NAME))
            cdk_deps = pyproject["tool"]["poetry"]["dependencies"].get("airbyte-cdk", None)
            if cdk_deps and isinstance(cdk_deps, dict) and "file-based" in cdk_deps.get("extras", []):
                return self.CDKTag.FILE
        if setup_py_file.exists():
            if "airbyte-cdk[file-based]" in (connector.code_directory / consts.SETUP_PY_FILE_NAME).read_text():
                return self.CDKTag.FILE
        return self.CDKTag.PYTHON

    def _run(self, connector: Connector) -> CheckResult:
        current_cdk_tags = [t for t in connector.metadata.get("tags", []) if t.startswith("cdk:")]
        expected_cdk_tag = self.get_expected_cdk_tag(connector)
        if not current_cdk_tags:
            return self.fail(
                connector=connector,
                message="CDK tag is missing in the metadata file",
            )
        if len(current_cdk_tags) > 1:
            return self.fail(
                connector=connector,
                message=f"Multiple CDK tags found in the metadata file: {current_cdk_tags}",
            )
        if current_cdk_tags[0] != expected_cdk_tag:
            return self.fail(
                connector=connector,
                message=f"Expected CDK tag '{self.get_expected_cdk_tag(connector)}' in the {consts.METADATA_FILE_NAME} file, but found '{current_cdk_tags[0]}'",
            )
        return self.pass_(
            connector=connector,
            message=f"CDK tag {self.get_expected_cdk_tag(connector)} is present in the metadata file",
        )


ENABLED_CHECKS = [
    ValidateMetadata(),
    CheckConnectorLanguageTag(),
    CheckConnectorCDKTag(),
]
