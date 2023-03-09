#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os

from ci_connector_ops.pipelines.contexts import ConnectorTestContext, ContextState
from ci_connector_ops.pipelines.models import ConnectorTestReport
from github import Github

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def update_commit_status_check(context: ConnectorTestContext, test_report: ConnectorTestReport = None):
    if context.is_local:
        context.logger.debug("Local run: no commit status sent to GitHub.")
        return
    github_context = f"Tests: {context.connector.technical_name}"
    error = None
    if context.state in [ContextState.CREATED, ContextState.INITIALIZED]:
        github_state = "pending"
        description = "Tests are being initialized..."
    elif context.state is ContextState.RUNNING:
        github_state = "pending"
        description = "Tests are running..."
    elif context.state is ContextState.FAILED:
        github_state = "error"
        description = "Something went wrong while running the tests."
    elif context.state is ContextState.FINISHED:
        if test_report is None:
            github_state = "error"
            description = "No report was provided at the end of the test execution."
            error = ValueError(description)
        elif test_report.success:
            github_state = "success"
            description = "All tests ran successfully."
        else:
            github_state = "failure"
            description = "Tests failed"
    else:
        github_state = "error"
        description = f"The {context.state.value} context state is not handled"
        error = ValueError(description)

    github_client = Github(os.environ["CI_GITHUB_ACCESS_TOKEN"])
    airbyte_repo = github_client.get_repo(AIRBYTE_GITHUB_REPO)
    airbyte_repo.get_commit(sha=context.git_revision).create_status(
        state=github_state, target_url=context.gha_workflow_run_url, description=description, context=github_context
    )
    context.logger.info(f"Created {github_state} status for commit {context.git_revision} on Github in {github_context} context.")
    if error:
        raise error
