#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.github import AIRBYTE_GITHUB_REPO
from dagger import Client, Directory, Secret


class GitPushChanges(Step):
    """
    A step to push changes to the remote repository.
    """

    title = "Push changes to the remote repository"

    GITHUB_REPO_URL = f"https://github.com/{AIRBYTE_GITHUB_REPO}.git"

    @property
    def ci_git_user(self) -> str:
        return self.context.ci_git_user

    @property
    def ci_github_access_token(self) -> str:
        return self.context.ci_github_access_token

    @property
    def dagger_client(self) -> Client:
        return self.context.dagger_client

    @property
    def git_branch(self) -> str:
        return self.context.git_branch

    @property
    def authenticated_repo_url(self) -> Secret:
        url = self.GITHUB_REPO_URL.replace("https://", f"https://{self.ci_git_user}:{self.ci_github_access_token}@")
        return self.dagger_client.set_secret("authenticated_repo_url", url)

    @property
    def airbyte_repo(self) -> Directory:
        return self.dagger_client.git(self.GITHUB_REPO_URL, keep_git_dir=True).branch(self.git_branch).tree()

    def get_commit_message(self, commit_message: str, skip_ci: bool) -> str:
        commit_message = f"🤖 {commit_message}"
        return f"{commit_message} [skip ci]" if skip_ci else commit_message

    async def _run(
        self, changed_directory: Directory, changed_directory_path: str, commit_message: str, skip_ci: bool = True
    ) -> StepResult:
        diff = (
            environments.with_git(self.dagger_client, self.context.ci_github_access_token_secret, self.ci_git_user)
            .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
            .with_mounted_directory("/airbyte", self.airbyte_repo)
            .with_workdir("/airbyte")
            .with_exec(["git", "checkout", self.git_branch])
            .with_mounted_directory(f"/airbyte/{changed_directory_path}", changed_directory)
            .with_exec(["git", "diff", "--name-only"])
        )

        if not await diff.stdout():
            return self.skip("No changes to push")

        commit_and_push = (
            diff.with_exec(["sh", "-c", "git remote set-url origin $AUTHENTICATED_REPO_URL"])
            .with_exec(["git", "add", "."])
            .with_exec(["git", "commit", "-m", self.get_commit_message(commit_message, skip_ci)])
            .with_exec(["git", "pull", "--rebase", "origin", self.git_branch])
            .with_exec(["git", "push"])
        )
        return await self.get_step_result(commit_and_push)


class GitPushEmptyCommit(GitPushChanges):
    """
    A step to push an empty commit to the remote repository.
    """

    title = "Push empty commit to the remote repository"

    def __init__(self, dagger_client, ci_git_user, ci_github_access_token, git_branch):
        self._dagger_client = dagger_client
        self._ci_github_access_token = ci_github_access_token
        self._ci_git_user = ci_git_user
        self._git_branch = git_branch
        self.ci_github_access_token_secret = dagger_client.set_secret("ci_github_access_token", ci_github_access_token)

    @property
    def dagger_client(self) -> Client:
        return self._dagger_client

    @property
    def ci_git_user(self) -> str:
        return self._ci_git_user

    @property
    def ci_github_access_token(self) -> Secret:
        return self._ci_github_access_token

    @property
    def git_branch(self) -> str:
        return self._git_branch

    async def _run(self, commit_message: str, skip_ci: bool = True) -> StepResult:
        push_empty_commit = (
            environments.with_git(self.dagger_client, self.ci_github_access_token_secret, self.ci_git_user)
            .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
            .with_mounted_directory("/airbyte", self.airbyte_repo)
            .with_workdir("/airbyte")
            .with_exec(["git", "checkout", self.git_branch])
            .with_exec(["sh", "-c", "git remote set-url origin $AUTHENTICATED_REPO_URL"])
            .with_exec(["git", "commit", "--allow-empty", "-m", self.get_commit_message(commit_message, skip_ci)])
            .with_exec(["git", "pull", "--rebase", "origin", self.git_branch])
            .with_exec(["git", "push"])
        )
        return await self.get_step_result(push_empty_commit)
