#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from pydantic import ValidationError
from source_acceptance_test import config

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
                {"connector_image": "foo", "acceptance_tests": {}, "test_mode": "extra-light"},
                None,
                pytest.raises(ValidationError),
                id="Invalid test mode: ValidationError",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}},
                config.Config(
                    connector_image="foo", acceptance_tests=config.AcceptanceTestConfigurations(), test_mode=config.Config.TestMode.light
                ),
                does_not_raise(),
                id="No test_mode: defaults to light, acceptance_tests field can be empty.",
            ),
            pytest.param(
                {"connector_image": "foo", "test_mode": "light", "acceptance_tests": {}},
                config.Config(
                    connector_image="foo", acceptance_tests=config.AcceptanceTestConfigurations(), test_mode=config.Config.TestMode.light
                ),
                does_not_raise(),
                id="Light test mode: acceptance_tests field can be empty.",
            ),
            pytest.param(
                {"connector_image": "foo", "test_mode": "medium", "acceptance_tests": {}},
                config.Config(
                    connector_image="foo", acceptance_tests=config.AcceptanceTestConfigurations(), test_mode=config.Config.TestMode.medium
                ),
                does_not_raise(),
                id="Medium test mode: acceptance_tests field can be empty.",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_mode": "strict"},
                None,
                pytest.raises(ValidationError),
                id="Strict test mode: acceptance_tests field can't be empty.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "test_mode": "strict",
                    "acceptance_tests": {
                        "connection": {"bypass_reason": "My good reason to bypass"},
                        "spec": {"bypass_reason": "My good reason to bypass"},
                        "basic_read": {"bypass_reason": "My good reason to bypass"},
                        "discovery": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                None,
                pytest.raises(ValidationError),
                id="Strict test mode: multiple tests are missing -> ValidationError",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "test_mode": "strict",
                    "acceptance_tests": {
                        "connection": {"bypass_reason": "My good reason to bypass"},
                        "spec": {"bypass_reason": "My good reason to bypass"},
                        "basic_read": {"bypass_reason": "My good reason to bypass"},
                        "full_refresh": {"bypass_reason": "My good reason to bypass"},
                        "incremental": {"bypass_reason": "My good reason to bypass"},
                        "discovery": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    test_mode=config.Config.TestMode.strict,
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        connection=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        spec=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        basic_read=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        full_refresh=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        incremental=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        discovery=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                    ),
                ),
                does_not_raise(),
                id="Strict test mode: all acceptance tests have a bypass reason -> No failure",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "test_mode": "strict",
                    "acceptance_tests": {
                        "spec": {"tests": [{"spec_path": "my-spec-path"}]},
                        "connection": {"bypass_reason": "My good reason to bypass"},
                        "basic_read": {"bypass_reason": "My good reason to bypass"},
                        "full_refresh": {"bypass_reason": "My good reason to bypass"},
                        "incremental": {"bypass_reason": "My good reason to bypass"},
                        "discovery": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    test_mode=config.Config.TestMode.strict,
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(tests=[config.SpecTestConfig(spec_path="my-spec-path")]),
                        connection=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        basic_read=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        full_refresh=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        incremental=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                        discovery=config.GenericTestConfig(bypass_reason="My good reason to bypass"),
                    ),
                ),
                does_not_raise(),
                id="Strict test mode: Only one test is configured, all other have a bypass reason -> No failure",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"tests": [{"spec_path": "my-spec-path"}], "bypass_reason": "I'm not bypassing"},
                        "connection": {"bypass_reason": "My good reason to bypass"},
                        "basic_read": {"bypass_reason": "My good reason to bypass"},
                        "full_refresh": {"bypass_reason": "My good reason to bypass"},
                        "incremental": {"bypass_reason": "My good reason to bypass"},
                        "discovery": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                None,
                pytest.raises(ValidationError),
                id="A test can't have a bypass reason and a configuration.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "test_mode": "strict",
                    "acceptance_tests": {
                        "spec": {"tests": [{"spec_path": "my-spec-path"}], "bypass_reason": "I'm not bypassing"},
                        "connection": {"bypass_reason": "My good reason to bypass"},
                        "basic_read": {"bypass_reason": "My good reason to bypass"},
                        "full_refresh": {"bypass_reason": "My good reason to bypass"},
                        "incremental": {"bypass_reason": "My good reason to bypass"},
                        "discovery": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                None,
                pytest.raises(ValidationError),
                id="Strict test mode: A test can't have a bypass reason and a configuration.",
            ),
        ],
    )
    def test_config_parsing(self, raw_config, expected_output_config, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config == expected_output_config
