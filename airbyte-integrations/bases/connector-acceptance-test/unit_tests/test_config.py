#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from connector_acceptance_test import config
from pydantic import ValidationError

from .conftest import does_not_raise


class TestConfig:
    @pytest.mark.parametrize(
        "raw_config, expected_output_config, expected_error",
        [
            pytest.param(
                {"connector_image": "foo", "tests": {"spec": [{"spec_path": "my-spec-path"}]}},
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(tests=[config.SpecTestConfig(spec_path="my-spec-path")])
                    ),
                ),
                does_not_raise(),
                id="Legacy config should be parsed without error.",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "extra-low"},
                None,
                pytest.raises(ValidationError),
                id="Invalid test mode: ValidationError",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "low"},
                config.Config(
                    connector_image="foo",
                    test_strictness_level=config.Config.TestStrictnessLevel.low,
                    acceptance_tests=config.AcceptanceTestConfigurations(),
                ),
                does_not_raise(),
                id="Valid test mode: low",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "high"},
                config.Config(
                    connector_image="foo",
                    test_strictness_level=config.Config.TestStrictnessLevel.high,
                    acceptance_tests=config.AcceptanceTestConfigurations(),
                ),
                does_not_raise(),
                id="Valid test mode: high",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(bypass_reason="My good reason to bypass")
                    ),
                ),
                does_not_raise(),
                id="A test can only have a bypass reason.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(bypass_reason="My good reason to bypass")
                    ),
                ),
                does_not_raise(),
                id="A test can only have a test configuration.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"tests": [{"spec_path": "my-spec-path"}], "bypass_reason": "I'm not bypassing"},
                    },
                },
                None,
                pytest.raises(ValidationError),
                id="A test can't have a bypass reason and a test configuration.",
            ),
        ],
    )
    def test_config_parsing(self, raw_config, expected_output_config, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config == expected_output_config

    @pytest.mark.parametrize(
        "legacy_config, expected_parsed_config",
        [
            pytest.param(
                {
                    "connector_image": "airbyte/source-pokeapi",
                    "tests": {
                        "connection": [
                            {"config_path": "integration_tests/config.json", "status": "succeed"},
                            {"config_path": "integration_tests/bad_config.json", "status": "failed"},
                        ],
                        "discovery": [{"config_path": "integration_tests/config.json"}],
                        "basic_read": [
                            {
                                "config_path": "integration_tests/config.json",
                                "configured_catalog_path": "integration_tests/configured_catalog.json",
                            }
                        ],
                    },
                },
                config.Config(
                    connector_image="airbyte/source-pokeapi",
                    test_strictness_level=config.Config.TestStrictnessLevel.low,
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        connection=config.GenericTestConfig(
                            tests=[
                                config.ConnectionTestConfig(
                                    config_path="integration_tests/config.json", status=config.ConnectionTestConfig.Status.Succeed
                                ),
                                config.ConnectionTestConfig(
                                    config_path="integration_tests/bad_config.json", status=config.ConnectionTestConfig.Status.Failed
                                ),
                            ]
                        ),
                        discovery=config.GenericTestConfig(tests=[config.DiscoveryTestConfig(config_path="integration_tests/config.json")]),
                        basic_read=config.GenericTestConfig(
                            tests=[
                                config.BasicReadTestConfig(
                                    config_path="integration_tests/config.json",
                                    configured_catalog_path="integration_tests/configured_catalog.json",
                                )
                            ]
                        ),
                    ),
                ),
                id="A legacy raw config is parsed into a new config structure without error.",
            ),
            pytest.param(
                {
                    "connector_image": "airbyte/source-pokeapi",
                    "test_strictness_level": "high",
                    "tests": {
                        "connection": [
                            {"config_path": "integration_tests/config.json", "status": "succeed"},
                            {"config_path": "integration_tests/bad_config.json", "status": "failed"},
                        ],
                        "discovery": [{"config_path": "integration_tests/config.json"}],
                        "basic_read": [
                            {
                                "config_path": "integration_tests/config.json",
                                "configured_catalog_path": "integration_tests/configured_catalog.json",
                            }
                        ],
                    },
                },
                config.Config(
                    connector_image="airbyte/source-pokeapi",
                    test_strictness_level=config.Config.TestStrictnessLevel.high,
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        connection=config.GenericTestConfig(
                            tests=[
                                config.ConnectionTestConfig(
                                    config_path="integration_tests/config.json", status=config.ConnectionTestConfig.Status.Succeed
                                ),
                                config.ConnectionTestConfig(
                                    config_path="integration_tests/bad_config.json", status=config.ConnectionTestConfig.Status.Failed
                                ),
                            ]
                        ),
                        discovery=config.GenericTestConfig(tests=[config.DiscoveryTestConfig(config_path="integration_tests/config.json")]),
                        basic_read=config.GenericTestConfig(
                            tests=[
                                config.BasicReadTestConfig(
                                    config_path="integration_tests/config.json",
                                    configured_catalog_path="integration_tests/configured_catalog.json",
                                )
                            ]
                        ),
                    ),
                ),
                id="A legacy raw config, with a test_strictness_level defined, is parsed into a new config structure without error.",
            ),
        ],
    )
    def test_legacy_config_migration(self, legacy_config, expected_parsed_config):
        assert config.Config.is_legacy(legacy_config)
        assert config.Config.parse_obj(legacy_config) == expected_parsed_config


class TestExpectedRecordsConfig:
    @pytest.mark.parametrize(
        "path, bypass_reason, expectation",
        [
            pytest.param("my_path", None, does_not_raise()),
            pytest.param(None, "Good bypass reason", does_not_raise()),
            pytest.param(None, None, pytest.raises(ValidationError)),
            pytest.param("my_path", "Good bypass reason", pytest.raises(ValidationError)),
        ],
    )
    def test_bypass_reason_behavior(self, path, bypass_reason, expectation):
        with expectation:
            config.ExpectedRecordsConfig(path=path, bypass_reason=bypass_reason)


class TestFileTypesConfig:
    @pytest.mark.parametrize(
        ("skip_test", "bypass_reason", "unsupported_types", "expectation"),
        (
            (True, None, None, does_not_raise()),
            (True, None, [config.UnsupportedFileTypeConfig(extension=".csv")], pytest.raises(ValidationError)),
            (False, None, None, does_not_raise()),
            (False, "bypass_reason", None, pytest.raises(ValidationError)),
            (False, "", None, pytest.raises(ValidationError)),
            (False, None, [config.UnsupportedFileTypeConfig(extension=".csv")], does_not_raise()),
        ),
    )
    def test_skip_test_behavior(self, skip_test, bypass_reason, unsupported_types, expectation):
        with expectation:
            config.FileTypesConfig(skip_test=skip_test, bypass_reason=bypass_reason, unsupported_types=unsupported_types)

    @pytest.mark.parametrize(
        ("extension", "expectation"),
        (
            (".csv", does_not_raise()),
            ("csv", pytest.raises(ValidationError)),
            (".", pytest.raises(ValidationError)),
            ("", pytest.raises(ValidationError)),
        ),
    )
    def test_extension_validation(self, extension, expectation):
        with expectation:
            config.UnsupportedFileTypeConfig(extension=extension)
