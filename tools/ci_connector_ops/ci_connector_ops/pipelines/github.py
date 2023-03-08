#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os

from github import Github

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def send_commit_status_check(commit_sha: str, state: str, gha_workflow_run_url: str, context: str, description: str = None):
    g = Github(os.environ["CI_GITHUB_ACCESS_TOKEN"])
    airbyte_repo = g.get_repo(AIRBYTE_GITHUB_REPO)
    airbyte_repo.get_commit(sha=commit_sha).create_status(
        state=state, target_url=gha_workflow_run_url, description=description, context=context
    )
