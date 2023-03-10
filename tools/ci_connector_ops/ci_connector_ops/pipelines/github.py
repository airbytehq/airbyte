#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext

from github import Github

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def update_commit_status_check(context: ConnectorTestContext):
    if context.is_local:
        context.logger.debug("Local run: no commit status sent to GitHub.")
        return

    github_context = f"Connector tests: {context.connector.technical_name}"
    error = None

    github_client = Github(os.environ["CI_GITHUB_ACCESS_TOKEN"])
    airbyte_repo = github_client.get_repo(AIRBYTE_GITHUB_REPO)
    airbyte_repo.get_commit(sha=context.git_revision).create_status(
        state=context.state.value["github_state"],
        target_url=context.gha_workflow_run_url,
        description=context.state.value["description"],
        context=github_context,
    )
    context.logger.info(
        f"Created {context.state.value['github_state']} status for commit {context.git_revision} on Github in {github_context} context."
    )
    if error:
        raise error
