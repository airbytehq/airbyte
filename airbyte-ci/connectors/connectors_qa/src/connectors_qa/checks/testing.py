# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from connector_ops.utils import Connector  # type: ignore
from connectors_qa.models import Check, CheckCategory, CheckResult
from pydash.collections import find


class TestingCheck(Check):
    category = CheckCategory.TESTING


class IntegrationTestsEnabledCheck(TestingCheck):
    name = "Medium to High Use Connectors must enable integration tests"
    description = "Medium to High Use Connectors must enable integration tests via the `connectorTestSuitesOptions.suite:integrationTests` in their respective metadata.yaml file to ensure that the connector is working as expected."

    def must_have_sandbox_config(self, connector: Connector) -> bool:
        return connector.cloud_usage in ["medium", "high"]

    def does_not_have_integration_enabled(self, connector: Connector) -> bool:
        metadata = connector.metadata
        connectorTestSuitesOptions = metadata.get("connectorTestSuitesOptions", [])
        integrationTests = find(connectorTestSuitesOptions, {"suite": "integrationTests"})
        return not integrationTests

    def _run(self, connector: Connector) -> CheckResult:
        if self.must_have_sandbox_config(connector) and self.does_not_have_integration_enabled(connector):
            return self.create_check_result(
                connector=connector,
                passed=False,
                message="Integration tests for medium/high use connectors require a sandbox config. Please provide a sandbox config in the metadata.yaml file.",
            )

        return self.create_check_result(
            connector=connector,
            passed=True,
            message="Integration tests for medium/high use connectors have a sandbox config.",
        )


ENABLED_CHECKS = [IntegrationTestsEnabledCheck()]
