#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.github import AIRBYTE_GITHUB_REPO
from dagger import Directory, Secret


class GitPushChanges(Step):
    """
    A step to push changes to the remote repository.
    """

    title = "Push changes to the remote repository"

    GITHUB_REPO_URL = f"https://github.com/{AIRBYTE_GITHUB_REPO}.git"

    @property
    def authenticated_repo_url(self) -> Secret:
        url = self.GITHUB_REPO_URL.replace("https://", f"https://{self.context.ci_git_user}:{self.context.ci_github_access_token}@")
        return self.context.dagger_client.set_secret("authenticated_repo_url", url)

    @property
    def airbyte_repo(self) -> Directory:
        return self.context.dagger_client.git(self.GITHUB_REPO_URL, keep_git_dir=True).branch(self.context.git_branch).tree()

    async def _run(
        self, changed_directory: Directory, changed_directory_path: str, commit_message: str, skip_ci: bool = True
    ) -> StepResult:
        commit_message = f"{commit_message} [skip ci]" if skip_ci else commit_message
        diff = (
            environments.with_git(self.context)
            .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
            .with_mounted_directory("/airbyte", self.airbyte_repo)
            .with_workdir("/airbyte")
            .with_exec(["git", "checkout", self.context.git_branch])
            .with_mounted_directory(f"/airbyte/{changed_directory_path}", changed_directory)
            .with_exec(["git", "diff", "--name-only"])
        )

        if not await diff.stdout():
            return self.skip("No changes to push")

        commit_and_push = (
            diff.with_exec(["sh", "-c", "git remote set-url origin $AUTHENTICATED_REPO_URL"])
            .with_exec(["git", "add", "."])
            .with_exec(["git", "commit", "-m", commit_message])
            .with_exec(["git", "push"])
        )
        return await self.get_step_result(commit_and_push)
