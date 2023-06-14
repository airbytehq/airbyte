#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Generic, List, Mapping, Optional, Set, TypeVar, Union

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.generics import GenericModel

config_path: str = Field(default="secrets/config.json", description="Path to a JSON object representing a valid connector configuration")
invalid_config_path: str = Field(description="Path to a JSON object representing an invalid connector configuration")
spec_path: str = Field(
    default="secrets/spec.json", description="Path to a JSON object representing the spec expected to be output by this connector"
)
configured_catalog_path: Optional[str] = Field(default=None, description="Path to configured catalog")
timeout_seconds: int = Field(default=None, description="Test execution timeout_seconds", ge=0)

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


class SpecTestConfig(BaseConfig):
    spec_path: str = spec_path
    config_path: str = config_path
    timeout_seconds: int = timeout_seconds
    backward_compatibility_tests_config: BackwardCompatibilityTestsConfig = Field(
        description="Configuration for the backward compatibility tests.", default=BackwardCompatibilityTestsConfig()
    )


class ConnectionTestConfig(BaseConfig):
    class Status(Enum):
        Succeed = "succeed"
        Failed = "failed"
        Exception = "exception"

    config_path: str = config_path
    status: Status = Field(Status.Succeed, description="Indicate if connection check should succeed with provided config")
    timeout_seconds: int = timeout_seconds


class DiscoveryTestConfig(BaseConfig):
    config_path: str = config_path
    timeout_seconds: int = timeout_seconds
    backward_compatibility_tests_config: BackwardCompatibilityTestsConfig = Field(
        description="Configuration for the backward compatibility tests.", default=BackwardCompatibilityTestsConfig()
    )


class ExpectedRecordsConfig(BaseModel):
    class Config:
        extra = "forbid"

    bypass_reason: Optional[str] = Field(description="Reason why this test is bypassed.")
    path: Optional[Path] = Field(description="File with expected records")
    extra_fields: bool = Field(False, description="Allow records to have other fields")
    exact_order: bool = Field(False, description="Ensure that records produced in exact same order")
    extra_records: bool = Field(
        True, description="Allow connector to produce extra records, but still enforce all records from the expected file to be produced"
    )

    @validator("exact_order", always=True)
    def validate_exact_order(cls, exact_order, values):
        if "extra_fields" in values and values["extra_fields"] and not exact_order:
            raise ValueError("exact_order must be on if extra_fields enabled")
        return exact_order

    @validator("extra_records", always=True)
    def validate_extra_records(cls, extra_records, values):
        if "extra_fields" in values and values["extra_fields"] and extra_records:
            raise ValueError("extra_records must be off if extra_fields enabled")
        return extra_records

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


ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]] = Field(
    description="For each stream, list of fields path ignoring in sequential reads test"
)


class BasicReadTestConfig(BaseConfig):
    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    empty_streams: Set[EmptyStreamConfiguration] = Field(
        default_factory=set, description="We validate that all streams has records. These are exceptions"
    )
    expect_records: Optional[ExpectedRecordsConfig] = Field(description="Expected records from the read")
    validate_schema: bool = Field(True, description="Ensure that records match the schema of the corresponding stream")
    fail_on_extra_columns: bool = Field(True, description="Fail if extra top-level properties (i.e. columns) are detected in records.")
    # TODO: remove this field after https://github.com/airbytehq/airbyte/issues/8312 is done
    validate_data_points: bool = Field(
        False, description="Set whether we need to validate that all fields in all streams contained at least one data point"
    )
    expect_trace_message_on_failure: bool = Field(True, description="Ensure that a trace message is emitted when the connector crashes")
    timeout_seconds: int = timeout_seconds
    ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]] = ignored_fields


class FullRefreshConfig(BaseConfig):
    """Full refresh test config

    Attributes:
        ignored_fields for each stream, list of fields path. Path should be in format "object_key/object_key2"
    """

    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    timeout_seconds: int = timeout_seconds
    ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]] = ignored_fields


class FutureStateConfig(BaseConfig):
    future_state_path: Optional[str] = Field(description="Path to a state file with values in far future")
    missing_streams: List[EmptyStreamConfiguration] = Field(default=[], description="List of missings streams with valid bypass reasons.")
    bypass_reason: Optional[str]


class IncrementalConfig(BaseConfig):
    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    cursor_paths: Optional[Mapping[str, List[Union[int, str]]]] = Field(
        description="For each stream, the path of its cursor field in the output state messages."
    )
    future_state: Optional[FutureStateConfig] = Field(description="Configuration for the future state.")
    timeout_seconds: int = timeout_seconds
    threshold_days: int = Field(
        description="Allow records to be emitted with a cursor value this number of days before the state cursor",
        default=0,
        ge=0,
    )
    skip_comprehensive_incremental_tests: Optional[bool] = Field(
        description="Determines whether to skip more granular testing for incremental syncs", default=False
    )

    class Config:
        smart_union = True


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


class Config(BaseConfig):
    class TestStrictnessLevel(str, Enum):
        high = "high"
        low = "low"

    cache_discovered_catalog: bool = Field(
        default=True, description="Enable or disable caching of discovered catalog for reuse in multiple tests."
    )
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
            {"connector_image": "my-connector-image", "tests": {"spec": [{"spec_path": "my/spec/path.json"}]}
        Gets converted to:
            {"connector_image": "my-connector-image", "acceptance_tests": {"spec": {"tests": [{"spec_path": "my/spec/path.json"}]}}

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
            if "ignored_fields" in basic_read_tests:
                basic_read_tests["ignored_fields"] = {
                    stream: [{"name": field_name} for field_name in ignore_fields]
                    for stream, ignore_fields in basic_read_tests["ignored_fields"].items()
                }
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
            logging.warn("The acceptance-test-config.yml file is in a legacy format. Please migrate to the latest format.")
            return cls.migrate_legacy_to_current_config(values)
        else:
            return values
