#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import Client, Container, Directory, Secret
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.steps import Step, StepResult


def with_git(dagger_client, ci_git_user: str = "octavia") -> Container:
    return (
        dagger_client.container()
        .from_("alpine:latest")
        .with_exec(
            sh_dash_c(
                [
                    "apk update",
                    "apk add git tar wget",
                    f"git config --global user.email {ci_git_user}@users.noreply.github.com",
                    f"git config --global user.name {ci_git_user}",
                    "git config --global --add --bool push.autoSetupRemote true",
                ]
            )
        )
        .with_workdir("/ghcli")
        .with_exec(
            sh_dash_c(
                [
                    "wget https://github.com/cli/cli/releases/download/v2.30.0/gh_2.30.0_linux_amd64.tar.gz -O ghcli.tar.gz",
                    "tar --strip-components=1 -xf ghcli.tar.gz",
                    "rm ghcli.tar.gz",
                    "cp bin/gh /usr/local/bin/gh",
                ]
            )
        )
    )


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
            with_git(self.dagger_client, self.context.ci_github_access_token_secret, self.ci_git_user)
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
            with_git(self.dagger_client, self.ci_github_access_token_secret, self.ci_git_user)
            .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
            .with_mounted_directory("/airbyte", self.airbyte_repo)
            .with_workdir("/airbyte")
            .with_exec(["git", "checkout", self.git_branch])
            .with_exec(sh_dash_c(["git remote set-url origin $AUTHENTICATED_REPO_URL"]))
            .with_exec(["git", "commit", "--allow-empty", "-m", self.get_commit_message(commit_message, skip_ci)])
            .with_exec(["git", "pull", "--rebase", "origin", self.git_branch])
            .with_exec(["git", "push"])
        )
        return await self.get_step_result(push_empty_commit)
