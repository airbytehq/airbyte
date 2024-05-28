# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from connectors_qa.checks import testing
from connectors_qa.models import CheckStatus

METADATA_CASE_NO_TEST_SUITE_OPTIONS = {}

METADATA_CASE_EMPTY_TEST_SUITE_OPTIONS = {
    "connectorTestSuitesOptions": [],
}

METADATA_CASE_NONE_TEST_SUITE_OPTIONS = {
    "connectorTestSuitesOptions": None,
}

METADATA_CASE_MISSING_INTEGRATION_TEST_SUITE_OPTIONS = {
    "connectorTestSuitesOptions": [
        {
            "suite": "unit",
            "testSecrets": {},
        },
    ],
}

METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_NO_SECRETS = {
    "connectorTestSuitesOptions": [
        {
            "suite": "integrationTests",
        },
    ],
}

METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_EMPTY_SECRETS = {
    "connectorTestSuitesOptions": [
        {
            "suite": "integrationTests",
            "testSecrets": {},
        },
    ],
}

METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_NONE_SECRETS = {
    "connectorTestSuitesOptions": [
        {
            "suite": "integrationTests",
            "testSecrets": None,
        },
    ],
}

METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS = {
    "connectorTestSuitesOptions": [
        {
            "suite": "integrationTests",
            "testSecrets": {
                "testSecret": "test"
            },
        },
        {
            "suite": "unit",
            "testSecrets": {},
        },
    ],
}

THRESHOLD_USAGE_VALUES = ["high", "medium"]
OTHER_USAGE_VALUES = ["low", "none", "unknown", None, ""]

DYNAMIC_INTEGRATION_TESTS_ENABLED_CASES = [
  METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS,
  METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_NONE_SECRETS,
  METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_EMPTY_SECRETS,
  METADATA_CASE_WITH_INTEGRATION_TEST_SUITE_OPTIONS_NO_SECRETS,
]

DYNAMIC_INTEGRATION_TESTS_DISABLED_CASES = [
    METADATA_CASE_NO_TEST_SUITE_OPTIONS,
    METADATA_CASE_EMPTY_TEST_SUITE_OPTIONS,
    METADATA_CASE_NONE_TEST_SUITE_OPTIONS,
    METADATA_CASE_MISSING_INTEGRATION_TEST_SUITE_OPTIONS,
]


class TestIntegrationTestsEnabledCheck:
    @pytest.mark.parametrize(
        "cases_to_test, usage_values_to_test, expected_result",
        [
            (
                DYNAMIC_INTEGRATION_TESTS_DISABLED_CASES + DYNAMIC_INTEGRATION_TESTS_ENABLED_CASES,
                OTHER_USAGE_VALUES,
                CheckStatus.PASSED
            ),
            (
                DYNAMIC_INTEGRATION_TESTS_ENABLED_CASES,
                THRESHOLD_USAGE_VALUES,
                CheckStatus.PASSED
            ),
            (
                DYNAMIC_INTEGRATION_TESTS_DISABLED_CASES,
                THRESHOLD_USAGE_VALUES,
                CheckStatus.FAILED
            )
        ],
    )
    def test_check_always_passes_when_usage_threshold_is_not_met(self, mocker, cases_to_test, usage_values_to_test, expected_result):
        for usage_value in usage_values_to_test:
            for metadata_case in cases_to_test:
                # Arrange
                connector = mocker.MagicMock(cloud_usage=usage_value, metadata=metadata_case)

                # Act        c
                result = testing.IntegrationTestsEnabledCheck()._run(connector)

                # Assert
                assert result.status == expected_result, f"Usage value: {usage_value}, metadata case: {metadata_case}, expected result: {expected_result}"
