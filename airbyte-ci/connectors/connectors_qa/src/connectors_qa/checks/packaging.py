# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import semver
import toml
from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult
from pydash.objects import get  # type: ignore


class PackagingCheck(Check):
    category = CheckCategory.PACKAGING


class CheckConnectorUsesPoetry(PackagingCheck):
    name = "Connectors must use Poetry for dependency management"
    description = "Connectors must use [Poetry](https://python-poetry.org/) for dependency management. This is to ensure that all connectors use a dependency management tool which locks dependencies and ensures reproducible installs."
    requires_metadata = False
    runs_on_released_connectors = False
    applies_to_connector_languages = [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.LOW_CODE,
    ]

    def _run(self, connector: Connector) -> CheckResult:
        if not (connector.code_directory / consts.PYPROJECT_FILE_NAME).exists():
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"{consts.PYPROJECT_FILE_NAME} file is missing",
            )
        if not (connector.code_directory / consts.POETRY_LOCK_FILE_NAME).exists():
            return self.fail(connector=connector, message=f"{consts.POETRY_LOCK_FILE_NAME} file is missing")
        if (connector.code_directory / consts.SETUP_PY_FILE_NAME).exists():
            return self.fail(
                connector=connector,
                message=f"{consts.SETUP_PY_FILE_NAME} file exists. Please remove it and use {consts.PYPROJECT_FILE_NAME} instead",
            )
        return self.pass_(
            connector=connector,
            message="Poetry is used for dependency management",
        )


class CheckPublishToPyPiIsEnabled(PackagingCheck):
    name = "Python connectors must have PyPi publishing enabled"
    description = f"Python connectors must have [PyPi](https://pypi.org/) publishing enabled in their `{consts.METADATA_FILE_NAME}` file. This is declared by setting `remoteRegistries.pypi.enabled` to `true` in {consts.METADATA_FILE_NAME}. This is to ensure that all connectors can be published to PyPi and can be used in `PyAirbyte`."
    applies_to_connector_languages = [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.LOW_CODE,
    ]
    applies_to_connector_types = ["source"]

    def _run(self, connector: Connector) -> CheckResult:
        publish_to_pypi_is_enabled = get(connector.metadata, "remoteRegistries.pypi.enabled", False)
        if not publish_to_pypi_is_enabled:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"PyPi publishing is not enabled. Please enable it in the {consts.METADATA_FILE_NAME} file",
            )
        return self.create_check_result(connector=connector, passed=True, message="PyPi publishing is enabled")


class CheckConnectorLicense(PackagingCheck):
    name = "Connectors must be licensed under MIT or Elv2"
    description = f"Connectors must be licensed under the MIT or Elv2 license. This is to ensure that all connectors are licensed under a permissive license. More details in our [License FAQ]({consts.LICENSE_FAQ_URL})."

    def _run(self, connector: Connector) -> CheckResult:
        metadata_license = get(connector.metadata, "license")
        if metadata_license is None:
            return self.fail(
                connector=connector,
                message="License is missing in the metadata file",
            )
        elif metadata_license.upper() not in consts.VALID_LICENSES:
            return self.fail(
                connector=connector,
                message=f"Connector is not using a valid license. Please use any of: {', '.join(consts.VALID_LICENSES)}",
            )
        else:
            return self.pass_(
                connector=connector,
                message=f"Connector is licensed under {metadata_license}",
            )


class CheckConnectorLicenseMatchInPyproject(PackagingCheck):
    name = f"Connector license in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file must match"
    description = f"Connectors license in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file must match. This is to ensure that all connectors are consistently licensed."
    applies_to_connector_languages = [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.LOW_CODE,
    ]

    def _run(self, connector: Connector) -> CheckResult:
        metadata_license = get(connector.metadata, "license")
        if metadata_license is None:
            return self.fail(
                connector=connector,
                message=f"License is missing in the {consts.METADATA_FILE_NAME} file",
            )
        if not (connector.code_directory / consts.PYPROJECT_FILE_NAME).exists():
            return self.fail(
                connector=connector,
                message=f"{consts.PYPROJECT_FILE_NAME} file is missing",
            )
        try:
            pyproject = toml.load((connector.code_directory / consts.PYPROJECT_FILE_NAME))
        except toml.TomlDecodeError:
            return self.fail(
                connector=connector,
                message=f"{consts.PYPROJECT_FILE_NAME} is invalid toml file",
            )

        poetry_license = get(pyproject, "tool.poetry.license")

        if poetry_license is None:
            return self.fail(
                connector=connector,
                message=f"Connector is missing license in {consts.PYPROJECT_FILE_NAME}. Please add it",
            )

        if poetry_license.lower() != metadata_license.lower():
            return self.fail(
                connector=connector,
                message=f"Connector is licensed under {poetry_license} in {consts.PYPROJECT_FILE_NAME}, but licensed under {metadata_license} in {consts.METADATA_FILE_NAME}. These two files have to be consistent",
            )

        return self.pass_(
            connector=connector,
            message=f"License in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file match",
        )


# TODO if more metadata.yaml to pyproject.toml field matching has to be done then create a generic class for this type of checks
class CheckConnectorVersionMatchInPyproject(PackagingCheck):
    name = f"Connector version in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file must match"
    description = f"Connector version in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file must match. This is to ensure that connector release is consistent."
    applies_to_connector_languages = [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.LOW_CODE,
    ]

    def _run(self, connector: Connector) -> CheckResult:
        metadata_version = get(connector.metadata, "dockerImageTag")
        if metadata_version is None:
            return self.fail(
                connector=connector,
                message=f"dockerImageTag field is missing in the {consts.METADATA_FILE_NAME} file",
            )

        if not (connector.code_directory / consts.PYPROJECT_FILE_NAME).exists():
            return self.fail(
                connector=connector,
                message=f"{consts.PYPROJECT_FILE_NAME} file is missing",
            )

        try:
            pyproject = toml.load((connector.code_directory / consts.PYPROJECT_FILE_NAME))
        except toml.TomlDecodeError:
            return self.fail(
                connector=connector,
                message=f"{consts.PYPROJECT_FILE_NAME} is invalid toml file",
            )

        poetry_version = get(pyproject, "tool.poetry.version")

        if poetry_version is None:
            return self.fail(
                connector=connector,
                message=f"Version field is missing in the {consts.PYPROJECT_FILE_NAME} file",
            )

        if poetry_version != metadata_version:
            return self.fail(
                connector=connector,
                message=f"Version is {metadata_version} in {consts.METADATA_FILE_NAME}, but version is {poetry_version} in {consts.PYPROJECT_FILE_NAME}. These two files have to be consistent",
            )

        return self.pass_(
            connector=connector,
            message=f"Version in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file match",
        )


class CheckVersionFollowsSemver(PackagingCheck):
    name = "Connector version must follow Semantic Versioning"
    description = f"Connector version must follow the Semantic Versioning scheme. This is to ensure that all connectors follow a consistent versioning scheme. Refer to our [Semantic Versioning for Connectors]({consts.SEMVER_FOR_CONNECTORS_DOC_URL}) for more details."

    def _run(self, connector: Connector) -> CheckResult:
        if "dockerImageTag" not in connector.metadata:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"dockerImageTag is missing in {consts.METADATA_FILE_NAME}",
            )
        try:
            semver.Version.parse(str(connector.metadata["dockerImageTag"]))
        except ValueError:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"Connector version {connector.metadata['dockerImageTag']} does not follow semantic versioning",
            )
        return self.create_check_result(
            connector=connector,
            passed=True,
            message="Connector version follows semantic versioning",
        )


ENABLED_CHECKS = [
    CheckConnectorUsesPoetry(),
    CheckConnectorLicense(),
    CheckConnectorLicenseMatchInPyproject(),
    CheckVersionFollowsSemver(),
    CheckConnectorVersionMatchInPyproject(),
    CheckPublishToPyPiIsEnabled(),
]
