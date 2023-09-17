#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Optional

from dagger import Container, Directory, Secret
from pipelines.actions import environments
from pipelines.bases import Step, StepResult, StepStatus
from pipelines.contexts import ConnectorContext
from pipelines.github import AIRBYTE_GITHUB_REPO


class AutoCommitStep(Step):
    skip_ci: bool = True
    GITHUB_REPO_URL = f"https://github.com/{AIRBYTE_GITHUB_REPO}.git"

    def __init__(self, context: ConnectorContext, container_with_airbyte_repo: Optional[Container] = None):
        super().__init__(context)
        self.context = context
        self.container_with_airbyte_repo = container_with_airbyte_repo if container_with_airbyte_repo else self.get_fresh_git_container()

    @property
    def airbyte_repo(self) -> Directory:
        return self.dagger_client.git(self.GITHUB_REPO_URL, keep_git_dir=True).branch(self.context.git_branch).tree()

    @property
    def authenticated_repo_url(self) -> Secret:
        url = self.GITHUB_REPO_URL.replace("https://", f"https://{self.context.ci_git_user}:{self.context.ci_github_access_token}@")
        return self.dagger_client.set_secret("authenticated_repo_url", url)

    @property
    def commit_message(self) -> str:
        commit_message = f"🤖 Autocommit on {self.context.connector.technical_name} - {self.title}"
        return f"[skip ci]: {commit_message} " if self.skip_ci else commit_message

    def get_fresh_git_container(self):
        return (
            environments.with_git(self.dagger_client, self.context.ci_github_access_token_secret, self.context.ci_git_user)
            .with_mounted_directory("/airbyte", self.airbyte_repo)
            .with_workdir("/airbyte")
            .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
            .with_exec(environments.sh_dash_c(["git remote set-url origin $AUTHENTICATED_REPO_URL"]))
        )

    async def commit_all_changes(self, container_with_latest_repo_state: Container) -> Container:
        return await container_with_latest_repo_state.with_exec(["git", "add", "."]).with_exec(["git", "commit", "-m", self.commit_message])

    async def get_connector_dir(self) -> Directory:
        if self.context.is_local:
            return await self.context.get_connector_dir()
        return self.container_with_airbyte_repo.directory(str(self.context.connector.code_directory))


class GitPushChanges(AutoCommitStep):
    """
    A step to push changes to the remote repository.
    """

    title = "Push changes to the remote repository"
    skip_ci = False

    async def _run(self) -> StepResult:
        commit_and_push = await (
            self.container_with_airbyte_repo.with_exec(["git", "pull", "--rebase", "origin", self.context.git_branch])
            .with_exec(["git", "commit", "--allow-empty", "-m", self.commit_message])
            .with_exec(["git", "push", "origin", f"HEAD:{self.context.git_branch}"])
        )

        return StepResult(self, StepStatus.SUCCESS, stdout=f"Changes pushed to {self.git_branch} branch", output_artifact=commit_and_push)
