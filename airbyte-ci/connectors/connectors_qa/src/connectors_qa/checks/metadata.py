# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import os
from datetime import datetime, timedelta

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

    def _run(self, connector: Connector) -> CheckResult:
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


class ValidateBreakingChangesDeadlines(MetadataCheck):
    """
    Verify that _if_ the most recent connector version has a breaking change,
    it's deadline is at least a week in the future.
    """

    name = "Breaking change deadline should be a week in the future"
    description = "If the connector version has a breaking change, the deadline field must be set to at least a week in the future."
    runs_on_released_connectors = False
    minimum_days_until_deadline = 7

    def _run(self, connector: Connector) -> CheckResult:

        # fetch the current branch version of the connector first.
        # we'll try and see if there are any breaking changes associated
        # with it next.
        current_version = connector.version
        if current_version is None:
            return self.fail(
                connector=connector,
                message="Can't verify breaking changes deadline: connector version is not defined.",
            )

        breaking_changes = connector.metadata.get("releases", {}).get("breakingChanges")

        if not breaking_changes:
            return self.pass_(
                connector=connector,
                message="No breaking changes found on this connector.",
            )

        current_version_breaking_changes = breaking_changes.get(current_version)

        if not current_version_breaking_changes:
            return self.pass_(
                connector=connector,
                message="No breaking changes found for the current version.",
            )

        upgrade_deadline = current_version_breaking_changes.get("upgradeDeadline")

        if not upgrade_deadline:
            return self.fail(
                connector=connector,
                message=f"No upgrade deadline found for the breaking changes in {current_version}.",
            )

        upgrade_deadline_datetime = datetime.strptime(upgrade_deadline, "%Y-%m-%d")
        one_week_from_now = datetime.utcnow() + timedelta(days=self.minimum_days_until_deadline)

        if upgrade_deadline_datetime <= one_week_from_now:
            return self.fail(
                connector=connector,
                message=f"The upgrade deadline for the breaking changes in {current_version} is less than {self.minimum_days_until_deadline} days from today. Please extend the deadline",
            )

        return self.pass_(connector=connector, message="The upgrade deadline is set to at least a week in the future")


class CheckConnectorMaxSecondsBetweenMessagesValue(MetadataCheck):
    name = "Certified source connector must have a value filled out for maxSecondsBetweenMessages in metadata"
    description = "Certified source connectors must have a value filled out for `maxSecondsBetweenMessages` in metadata. This value represents the maximum number of seconds we could expect between messages for API connectors. And it's used by platform to tune connectors heartbeat timeout. The value must be set in the 'data' field in connector's `metadata.yaml` file."
    applies_to_connector_types = ["source"]
    applies_to_connector_support_levels = ["certified"]

    def _run(self, connector: Connector) -> CheckResult:
        max_seconds_between_messages = connector.metadata.get("maxSecondsBetweenMessages")
        if not max_seconds_between_messages:
            return self.fail(
                connector=connector,
                message="Missing required for certified connectors field 'maxSecondsBetweenMessages'",
            )
        return self.pass_(
            connector=connector,
            message="Value for maxSecondsBetweenMessages is set",
        )


ENABLED_CHECKS = [
    ValidateMetadata(),
    CheckConnectorLanguageTag(),
    CheckConnectorCDKTag(),
    ValidateBreakingChangesDeadlines(),
    CheckConnectorMaxSecondsBetweenMessagesValue(),
]
