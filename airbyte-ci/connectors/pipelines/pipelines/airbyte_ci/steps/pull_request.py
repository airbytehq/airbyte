# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING

from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.helpers import github
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Iterable, Optional


class CreateOrUpdatePullRequest(Step):
    context: ConnectorContext
    pull: bool

    title = "Create or update pull request on Airbyte repository"

    def __init__(
        self,
        context: PipelineContext,
        skip_ci: bool,
        labels: Optional[Iterable[str]] = None,
    ) -> None:
        super().__init__(context)
        self.skip_ci = skip_ci
        self.labels = labels or []

    async def _run(
        self,
        modified_repo_files: Iterable[Path],
        branch_id: str,
        commit_message: str,
        pr_title: str,
        pr_body: str,
    ) -> StepResult:
        if self.context.ci_github_access_token is None:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr="No github access token provided")

        try:
            pr = github.create_or_update_github_pull_request(
                modified_repo_files,
                self.context.ci_github_access_token.value,
                branch_id,
                commit_message,
                pr_title,
                pr_body,
                logger=self.logger,
                skip_ci=self.skip_ci,
                labels=self.labels,
            )
        except Exception as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e), exc_info=e)

        return StepResult(step=self, status=StepStatus.SUCCESS, output=pr)
