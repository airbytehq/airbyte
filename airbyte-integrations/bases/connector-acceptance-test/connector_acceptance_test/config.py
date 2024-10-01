#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generic, List, Mapping, Optional, Set, TypeVar

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.generics import GenericModel

config_path: str = Field(default="secrets/config.json", description="Path to a JSON object representing a valid connector configuration")
invalid_config_path: str = Field(description="Path to a JSON object representing an invalid connector configuration")
spec_path: str = Field(
    default="secrets/spec.json", description="Path to a JSON object representing the spec expected to be output by this connector"
)
configured_catalog_path: Optional[str] = Field(default=None, description="Path to configured catalog")
timeout_seconds: int = Field(default=None, description="Test execution timeout_seconds", ge=0)
deployment_mode: Optional[str] = Field(default=None, description="Deployment mode to run the test in", regex=r"^(cloud|oss)$")

SEMVER_REGEX = r"(0|(?:[1-9]\d*))(?:\.(0|(?:[1-9]\d*))(?:\.(0|(?:[1-9]\d*)))?(?:\-([\w][\w\.\-_]*))?)?"
ALLOW_LEGACY_CONFIG = True


class BaseConfig(BaseModel):
    class Config:
        extra = "forbid"


TestConfigT = TypeVar("TestConfigT")


class BackwardCompatibilityTestsConfig(BaseConfig):
    previous_connector_version: str = Field(
        regex=SEMVER_REGEX, default="latest", description="Previous connector version to use for backward compatibility tests."
    )
    disable_for_version: Optional[str] = Field(
        regex=SEMVER_REGEX, default=None, description="Disable backward compatibility tests for a specific connector version."
    )


class OAuthTestConfig(BaseConfig):
    oauth = Field(True, description="Allow source to have another default method that OAuth.")
    bypass_reason: Optional[str] = Field(description="Reason why OAuth is not default method.")

    @validator("oauth", always=True)
    def validate_oauth(cls, oauth, values):
        if oauth is False and not values.get("bypass_reason"):
            raise ValueError("Please provide a bypass reason for Auth default method")
        return oauth


class SpecTestConfig(BaseConfig):
    spec_path: str = spec_path
    config_path: str = config_path
    timeout_seconds: int = timeout_seconds
    deployment_mode: Optional[str] = deployment_mode
    backward_compatibility_tests_config: BackwardCompatibilityTestsConfig = Field(
        description="Configuration for the backward compatibility tests.", default=BackwardCompatibilityTestsConfig()
    )
    auth_default_method: Optional[OAuthTestConfig] = Field(description="Auth default method details.")


class ConnectionTestConfig(BaseConfig):
    class Status(Enum):
        Succeed = "succeed"
        Failed = "failed"
        Exception = "exception"

    config_path: str = config_path
    status: Status = Field(Status.Succeed, description="Indicate if connection check should succeed with provided config")
    timeout_seconds: int = timeout_seconds
    deployment_mode: Optional[str] = deployment_mode


class DiscoveryTestConfig(BaseConfig):
    config_path: str = config_path
    timeout_seconds: int = timeout_seconds
    deployment_mode: Optional[str] = deployment_mode
    backward_compatibility_tests_config: BackwardCompatibilityTestsConfig = Field(
        description="Configuration for the backward compatibility tests.", default=BackwardCompatibilityTestsConfig()
    )
    validate_primary_keys_data_type: bool = Field(True, description="Ensure correct primary keys data type")


class ExpectedRecordsConfig(BaseModel):
    class Config:
        extra = "forbid"

    bypass_reason: Optional[str] = Field(description="Reason why this test is bypassed.")
    path: Optional[Path] = Field(description="File with expected records")
    exact_order: bool = Field(False, description="Ensure that records produced in exact same order")

    @validator("path", always=True)
    def no_bypass_reason_when_path_is_set(cls, path, values):
        if path and values.get("bypass_reason"):
            raise ValueError("You can't set a bypass_reason if a path is set")
        if not path and not values.get("bypass_reason"):
            raise ValueError("A path or a bypass_reason must be set")
        return path


class EmptyStreamConfiguration(BaseConfig):
    name: str
    bypass_reason: Optional[str] = Field(default=None, description="Reason why this stream is considered empty.")

    def __hash__(self):  # make it hashable
        return hash((type(self),) + tuple(self.__dict__.values()))


class IgnoredFieldsConfiguration(BaseConfig):
    name: str
    bypass_reason: Optional[str] = Field(default=None, description="Reason why this field is considered ignored.")


class NoPrimaryKeyConfiguration(BaseConfig):
    name: str
    bypass_reason: Optional[str] = Field(default=None, description="Reason why this stream does not support a primary key")


class AllowedHostsConfiguration(BaseConfig):
    bypass_reason: Optional[str] = Field(
        default=None, description="Reason why the Metadata `AllowedHosts` check should be skipped for this certified connector."
    )


class SuggestedStreamsConfiguration(BaseConfig):
    bypass_reason: Optional[str] = Field(
        default=None, description="Reason why the Metadata `SuggestedStreams` check should be skipped for this certified connector."
    )


class UnsupportedFileTypeConfig(BaseConfig):
    extension: str
    bypass_reason: Optional[str] = Field(description="Reason why this type is considered unsupported.")

    @validator("extension", always=True)
    def extension_properly_formatted(cls, extension: str) -> str:
        if not extension.startswith(".") or len(extension) < 2:
            raise ValueError("Please provide a valid file extension (e.g. '.csv').")
        return extension


class FileTypesConfig(BaseConfig):
    bypass_reason: Optional[str] = Field(description="Reason why this test is bypassed.")
    unsupported_types: Optional[List[UnsupportedFileTypeConfig]] = Field(description="A list of unsupported file types for the source.")
    skip_test: Optional[bool] = Field(False, description="Skip file-based connector specific test.")

    @validator("skip_test", always=True)
    def no_unsupported_types_when_skip_test(cls, skip_test: bool, values: Dict[str, Any]) -> bool:
        if skip_test and values.get("unsupported_types"):
            raise ValueError("You can't set 'unsupported_types' if the test is skipped.")
        if not skip_test and values.get("bypass_reason") is not None:
            raise ValueError("You can't set 'bypass_reason' if the test is not skipped.")
        return skip_test


class ClientContainerConfig(BaseConfig):
    secrets_path: str = Field(None, description="Path in the setup/teardown container at which to copy connector secrets.")
    client_container_dockerfile_path: str = Field(
        None, description="Path to Dockerfile to run before each test for which a config is provided."
    )
    setup_command: Optional[List[str]] = Field(None, description="Command for running the setup/teardown container for setup.")
    teardown_command: Optional[List[str]] = Field(None, description="Command for running the setup/teardown container for teardown.")
    between_syncs_command: Optional[List[str]] = Field(None, description="Command to run between syncs that occur in a test.")
    final_teardown_command: Optional[List[str]] = Field(None, description="Command for running teardown after all tests have run.")


class BasicReadTestConfig(BaseConfig):
    config_path: str = config_path
    deployment_mode: Optional[str] = deployment_mode
    configured_catalog_path: Optional[str] = configured_catalog_path
    empty_streams: Set[EmptyStreamConfiguration] = Field(
        default_factory=set, description="We validate that all streams has records. These are exceptions"
    )
    expect_records: Optional[ExpectedRecordsConfig] = Field(description="Expected records from the read")
    validate_schema: bool = Field(True, description="Ensure that records match the schema of the corresponding stream")
    validate_stream_statuses: bool = Field(None, description="Ensure that all streams emit status messages")
    validate_state_messages: bool = Field(True, description="Ensure that state messages emitted as expected")
    validate_primary_keys_data_type: bool = Field(True, description="Ensure correct primary keys data type")
    fail_on_extra_columns: bool = Field(True, description="Fail if extra top-level properties (i.e. columns) are detected in records.")
    # TODO: remove this field after https://github.com/airbytehq/airbyte/issues/8312 is done
    validate_data_points: bool = Field(
        False, description="Set whether we need to validate that all fields in all streams contained at least one data point"
    )
    expect_trace_message_on_failure: bool = Field(True, description="Ensure that a trace message is emitted when the connector crashes")
    timeout_seconds: int = timeout_seconds
    file_types: Optional[FileTypesConfig] = Field(
        default_factory=FileTypesConfig,
        description="For file-based connectors, unsupported by source file types can be configured or a test can be skipped at all",
    )
    client_container_config: Optional[ClientContainerConfig] = Field(
        description="Information required to run a client Docker container before each test.",
    )


class FullRefreshConfig(BaseConfig):
    """Full refresh test config

    Attributes:
        ignored_fields for each stream, list of fields path. Path should be in format "object_key/object_key2"
    """

    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    timeout_seconds: int = timeout_seconds
    deployment_mode: Optional[str] = deployment_mode
    ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]] = Field(
        description="For each stream, list of fields path ignoring in sequential reads test"
    )
    client_container_config: Optional[ClientContainerConfig] = Field(
        description="Information required to run a client Docker container before each test.",
    )


class FutureStateCursorFormatStreamConfiguration(BaseConfig):
    name: str
    format: Optional[str] = Field(default=None, description="Expected format of the cursor value")


class FutureStateCursorFormatConfiguration(BaseConfig):
    format: Optional[str] = Field(
        default=None,
        description="The default format of the cursor value will be used for all streams except those defined in the streams section",
    )
    streams: List[FutureStateCursorFormatStreamConfiguration] = Field(
        default_factory=list, description="Expected cursor value format for a particular stream"
    )


class FutureStateConfig(BaseConfig):
    future_state_path: Optional[str] = Field(description="Path to a state file with values in far future")
    missing_streams: List[EmptyStreamConfiguration] = Field(default=[], description="List of missing streams with valid bypass reasons.")
    bypass_reason: Optional[str]
    cursor_format: Optional[FutureStateCursorFormatConfiguration] = Field(
        default_factory=FutureStateCursorFormatConfiguration,
        description=("Expected cursor format"),
    )


class IncrementalConfig(BaseConfig):
    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    future_state: Optional[FutureStateConfig] = Field(description="Configuration for the future state.")
    timeout_seconds: int = timeout_seconds
    deployment_mode: Optional[str] = deployment_mode
    skip_comprehensive_incremental_tests: Optional[bool] = Field(
        description="Determines whether to skip more granular testing for incremental syncs", default=False
    )
    client_container_config: Optional[ClientContainerConfig] = Field(
        description="Information required to run a client Docker container before each test.",
    )

    class Config:
        smart_union = True


class ConnectorAttributesConfig(BaseConfig):
    """
    Config that is used to verify that a connector and its streams uphold certain behavior and features that are
    required to maintain enterprise-level standard of quality.

    Attributes:
        streams_without_primary_key: A list of streams where a primary key is not available from the API or is not relevant to the record
    """

    timeout_seconds: int = timeout_seconds
    config_path: str = config_path

    streams_without_primary_key: Optional[List[NoPrimaryKeyConfiguration]] = Field(
        description="Streams that do not support a primary key such as reports streams"
    )
    allowed_hosts: Optional[AllowedHostsConfiguration] = Field(
        description="Used to bypass checking the `allowedHosts` field in a source's `metadata.yaml` when all external hosts should be reachable."
    )
    suggested_streams: Optional[SuggestedStreamsConfiguration] = Field(
        description="Used to bypass checking the `suggestedStreams` field in a source's `metadata.yaml` when certified source doesn't have any."
    )


class TestConnectorDocumentationConfig(BaseConfig):
    timeout_seconds: int = timeout_seconds
    config_path: str = config_path


class GenericTestConfig(GenericModel, Generic[TestConfigT]):
    bypass_reason: Optional[str]
    tests: Optional[List[TestConfigT]]

    @validator("tests", always=True)
    def no_bypass_reason_when_tests_is_set(cls, tests, values):
        if tests and values.get("bypass_reason"):
            raise ValueError("You can't set a bypass_reason if tests are set.")
        return tests


class AcceptanceTestConfigurations(BaseConfig):
    spec: Optional[GenericTestConfig[SpecTestConfig]]
    connection: Optional[GenericTestConfig[ConnectionTestConfig]]
    discovery: Optional[GenericTestConfig[DiscoveryTestConfig]]
    basic_read: Optional[GenericTestConfig[BasicReadTestConfig]]
    full_refresh: Optional[GenericTestConfig[FullRefreshConfig]]
    incremental: Optional[GenericTestConfig[IncrementalConfig]]
    connector_attributes: Optional[GenericTestConfig[ConnectorAttributesConfig]]
    connector_documentation: Optional[GenericTestConfig[TestConnectorDocumentationConfig]]
    client_container_config: Optional[ClientContainerConfig]


class Config(BaseConfig):
    class TestStrictnessLevel(str, Enum):
        high = "high"
        low = "low"

    connector_image: str = Field(description="Docker image to test, for example 'airbyte/source-hubspot:dev'")
    acceptance_tests: AcceptanceTestConfigurations = Field(description="List of the acceptance test to run with their configs")
    base_path: Optional[str] = Field(description="Base path for all relative paths")
    test_strictness_level: Optional[TestStrictnessLevel] = Field(
        default=TestStrictnessLevel.low,
        description="Corresponds to a strictness level of the test suite and will change which tests are mandatory for a successful run.",
    )
    custom_environment_variables: Optional[Mapping] = Field(
        default={}, description="Mapping of custom environment variables to pass to the connector under test."
    )

    @staticmethod
    def is_legacy(config: dict) -> bool:
        """Check if a configuration is 'legacy'.
        We consider it is legacy if a 'tests' field exists at its root level (prior to v0.2.12).

        Args:
            config (dict): A configuration

        Returns:
            bool: Whether the configuration is legacy.
        """
        return "tests" in config

    @staticmethod
    def migrate_legacy_to_current_config(legacy_config: dict) -> dict:
        """Convert configuration structure created prior to v0.2.12 into the current structure.
        e.g.
        This structure:
            {"connector_image": "my-connector-image", "tests": {"spec": [{"spec_path": "my/spec/path.json"}]}}
        Gets converted to:
            {"connector_image": "my-connector-image", "acceptance_tests": {"spec": {"tests": [{"spec_path": "my/spec/path.json"}]}}}

        Args:
            legacy_config (dict): A legacy configuration

        Returns:
            dict: A migrated configuration
        """
        migrated_config = deepcopy(legacy_config)
        migrated_config.pop("tests")
        migrated_config["acceptance_tests"] = {}
        for test_name, test_configs in legacy_config["tests"].items():
            migrated_config["acceptance_tests"][test_name] = {"tests": test_configs}
        for basic_read_tests in migrated_config["acceptance_tests"].get("basic_read", {}).get("tests", []):
            if "empty_streams" in basic_read_tests:
                basic_read_tests["empty_streams"] = [
                    {"name": empty_stream_name} for empty_stream_name in basic_read_tests.get("empty_streams", [])
                ]
        for full_refresh_test in migrated_config["acceptance_tests"].get("full_refresh", {}).get("tests", []):
            if "ignored_fields" in full_refresh_test:
                full_refresh_test["ignored_fields"] = {
                    stream: [{"name": field_name} for field_name in ignore_fields]
                    for stream, ignore_fields in full_refresh_test["ignored_fields"].items()
                }
        for incremental_test in migrated_config["acceptance_tests"].get("incremental", {}).get("tests", []):
            if "future_state_path" in incremental_test:
                incremental_test["future_state"] = {"future_state_path": incremental_test.pop("future_state_path")}
        return migrated_config

    @root_validator(pre=True)
    def legacy_format_adapter(cls, values: dict) -> dict:
        """Root level validator executed 'pre' field validation to migrate a legacy config to the current structure.

        Args:
            values (dict): The raw configuration.

        Returns:
            dict: The migrated configuration if needed.
        """
        if ALLOW_LEGACY_CONFIG and cls.is_legacy(values):
            logging.warning("The acceptance-test-config.yml file is in a legacy format. Please migrate to the latest format.")
            return cls.migrate_legacy_to_current_config(values)
        else:
            return values
