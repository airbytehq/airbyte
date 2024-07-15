#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific manifest only connector given a test context."""

from pipelines.airbyte_ci.connectors.build_image.steps.manifest_only_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests, IncrementalAcceptanceTests, LiveTests
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """
    Get all the tests steps for a Python connector.
    """

    return [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
                step=AcceptanceTests(
                    context,
                    concurrent_test_run=context.concurrent_cat,
                    secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.ACCEPTANCE),
                ),
                args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.CONNECTOR_LIVE_TESTS,
                step=LiveTests(context),
                args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INCREMENTAL_ACCEPTANCE,
                step=IncrementalAcceptanceTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.ACCEPTANCE)),
                args=lambda results: {"current_acceptance_tests_result": results[CONNECTOR_TEST_STEP_ID.ACCEPTANCE]},
                depends_on=[CONNECTOR_TEST_STEP_ID.ACCEPTANCE],
            )
        ],
    ]
