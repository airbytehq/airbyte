# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import os

from connector_ops.utils import Connector  # type: ignore
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

    def _run(self, connector: Connector) -> CheckResult:
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

        if (connector.code_directory / consts.SETUP_PY_FILE_NAME).exists() or (
            connector.code_directory / consts.PYPROJECT_FILE_NAME
        ).exists():
            expected_language = self.PYTHON_LANGUAGE_TAG
        elif (connector.code_directory / consts.GRADLE_FILE_NAME).exists():
            expected_language = self.JAVA_LANGUAGE_TAG
        else:
            return self.fail(
                connector=connector,
                message="Could not infer the language tag from the connector directory",
            )
        if current_language_tag != expected_language:
            return self.fail(
                connector=connector,
                message=f"Expected language tag '{expected_language}' in the {consts.METADATA_FILE_NAME} file, but found '{current_language_tag}'",
            )
        return self.pass_(
            connector=connector,
            message=f"Language tag {expected_language} is present in the metadata file",
        )


ENABLED_CHECKS = [
    ValidateMetadata(),
    # Disabled until metadata are globally cleaned up
    # CheckConnectorLanguageTag()
]
