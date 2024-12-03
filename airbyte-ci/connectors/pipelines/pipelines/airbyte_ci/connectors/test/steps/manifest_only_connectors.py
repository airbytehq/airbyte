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
from pipelines.airbyte_ci.connectors.test.steps.python_connectors import PytestStep
from pipelines.models.steps import STEP_PARAMS


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """
    Get all the tests steps for a Python connector.
    """

    return [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UNIT,
                step=ManifestOnlyConnectorUnitTests(context),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
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

class ManifestOnlyConnectorUnitTests(PytestStep):
    """A step to run unit tests for a manifest-only connector"""

    title = "Manifest-only unit tests"
    test_directory_name = "unit_tests"

    # No coverage reporting needed since we're just testing components.py
    common_test_dependencies = ["pytest"]

    @property
    def default_params(self) -> STEP_PARAMS:
        """Default pytest options without coverage computation"""

        return super().default_params
