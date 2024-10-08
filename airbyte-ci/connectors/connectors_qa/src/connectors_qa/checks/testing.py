# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from connector_ops.utils import Connector  # type: ignore
from connectors_qa.models import Check, CheckCategory, CheckResult
from pydash.collections import find  # type: ignore


class TestingCheck(Check):
    category = CheckCategory.TESTING


class AcceptanceTestsEnabledCheck(TestingCheck):
    applies_to_connector_cloud_usage = ["medium", "high"]
    applies_to_connector_types = ["source"]
    name = "Medium to High Use Connectors must enable acceptance tests"
    description = "Medium to High Use Connectors must enable acceptance tests via the `connectorTestSuitesOptions.suite:acceptanceTests` in their respective metadata.yaml file to ensure that the connector is working as expected."
    test_suite_name = "acceptanceTests"

    def does_not_have_acceptance_tests_enabled(self, connector: Connector) -> bool:
        metadata = connector.metadata
        connector_test_suites_options = metadata.get("connectorTestSuitesOptions", [])
        acceptance_tests_suite = find(connector_test_suites_options, {"suite": self.test_suite_name})
        return bool(acceptance_tests_suite) is False

    def _run(self, connector: Connector) -> CheckResult:
        if self.does_not_have_acceptance_tests_enabled(connector):
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"The {self.test_suite_name} test suite must be enabled for medium/high use connectors. Please enable this test suite in the connectorTestSuitesOptions field of the metadata.yaml file.",
            )
        return self.create_check_result(
            connector=connector,
            passed=True,
            message=f"{connector.cloud_usage} cloud usage connector has enabled {self.test_suite_name}.",
        )


ENABLED_CHECKS = [AcceptanceTestsEnabledCheck()]
