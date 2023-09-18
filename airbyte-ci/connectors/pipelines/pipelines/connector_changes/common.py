#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from connector_ops.utils import METADATA_FILE_NAME
from dagger import Container, Directory, Secret
from pipelines.actions import environments
from pipelines.bases import Step, StepResult
from pipelines.consts import AIRBYTE_GITHUB_REPO_URL
from pipelines.contexts import ConnectorContext


class ConnectorChangeStep(Step):
    def __init__(
        self,
        context: ConnectorContext,
        export_changes_to_host: bool,
        container_with_airbyte_repo: Optional[Container] = None,
        commit: bool = False,
        push: bool = False,
        skip_ci=True,
    ):
        super().__init__(context)
        self.export_changes_to_host = export_changes_to_host
        self.container_with_airbyte_repo = container_with_airbyte_repo
        self.commit = commit
        self.push = push
        self.skip_ci = skip_ci

    @property
    def modified_paths(self) -> List[str]:
        return [self.context.connector.code_directory]

    async def get_airbyte_local_repo(self) -> Directory:
        return self.context.get_repo_dir()

    def get_airbyte_remote_repo(self) -> Directory:
        return self.dagger_client.git(AIRBYTE_GITHUB_REPO_URL, keep_git_dir=True).branch(self.context.git_branch).tree()

    async def get_airbyte_repo(self):
        if self.context.is_local:
            return await self.get_airbyte_local_repo()
        return self.get_airbyte_remote_repo()

    @property
    def authenticated_repo_url(self) -> Secret:
        if self.context.ci_git_user is None or self.context.ci_github_access_token is None:
            raise Exception("Missing CI git user or CI github access token")
        url = self.GITHUB_REPO_URL.replace("https://", f"https://{self.context.ci_git_user}:{self.context.ci_github_access_token}@")
        return self.dagger_client.set_secret("authenticated_repo_url", url)

    @property
    def commit_message(self) -> str:
        commit_message = f"🤖 {self.context.connector.technical_name} - {self.title}"
        return f"[skip ci]: {commit_message} " if self.skip_ci else commit_message

    async def get_fresh_git_container(self, authenticated: bool = False) -> Container:
        if not authenticated:
            return (
                environments.with_git(self.dagger_client, self.context.ci_git_user)
                .with_mounted_directory("/airbyte", (await self.get_airbyte_repo()))
                .with_workdir("/airbyte")
            )
        else:
            return (
                await self.get_fresh_git_container(authenticated=False)
                .with_secret_variable("GITHUB_TOKEN", self.context.ci_github_access_token_secret)
                .with_secret_variable("AUTHENTICATED_REPO_URL", self.authenticated_repo_url)
                .with_exec(environments.sh_dash_c(["git remote set-url origin $AUTHENTICATED_REPO_URL"]))
            )

    def commit_connector_changes(self, container_with_latest_repo_state: Container) -> Container:
        return container_with_latest_repo_state.with_exec(["git", "add", str(self.context.connector.code_directory)]).with_exec(
            ["git", "commit", "-m", self.commit_message]
        )

    def push(self, container_with_latest_repo_state: Container) -> Container:
        return container_with_latest_repo_state.with_exec(["git", "pull", "--rebase", "origin", self.context.git_branch]).with_exec(
            ["git", "push", "origin", f"HEAD:{self.context.git_branch}"]
        )

    async def get_connector_dir(self) -> Directory:
        return (await self.get_airbyte_repo()).directory(str(self.context.connector.code_directory))

    async def _run(self) -> StepResult:
        self.container_with_airbyte_repo = (
            self.container_with_airbyte_repo if self.container_with_airbyte_repo is not None else await self.get_fresh_git_container()
        )
        change_result = await self.make_connector_change()
        self.container_with_airbyte_repo = change_result.output_artifact
        if self.commit:
            self.container_with_airbyte_repo = await self.commit_connector_changes(self.container_with_airbyte_repo)
            self.logger.info("Changes committed.")
        if self.push:
            self.container_with_airbyte_repo = self.push(self.container_with_airbyte_repo)
            self.logger.info("Changes pushed.")
        if self.export_changes_to_host:
            for modified_path in self.modified_paths:
                if modified_path.is_dir():
                    await self.container_with_airbyte_repo.directory(str(modified_path)).export(str(modified_path))
                else:
                    await self.container_with_airbyte_repo.file(str(modified_path)).export(str(modified_path))

            self.logger.info("Changes exported back to host.")
        return change_result

    @abstractmethod
    async def make_connector_change(self, container_with_airbyte_repo) -> StepResult:
        raise NotImplementedError()


class MetadataUpdateStep(ConnectorChangeStep):
    @property
    def modified_paths(self) -> List[Path]:
        return [self.context.connector.code_directory / METADATA_FILE_NAME]

    @property
    def metadata_path(self) -> str:
        return str(self.context.connector.code_directory / METADATA_FILE_NAME)

    async def get_current_metadata(self) -> Dict:
        return yaml.safe_load(await self.container_with_airbyte_repo.file(self.metadata_path).contents())

    @abstractmethod
    async def get_updated_metadata(self) -> str:
        raise NotImplementedError()

    async def get_container_with_updated_metadata(self, container_with_airbyte_repo: Container) -> Container:
        new_metadata = await self.get_updated_metadata()
        absolute_path_to_new_metadata = f"/airbyte/{self.context.connector.code_directory}/{METADATA_FILE_NAME}"
        return container_with_airbyte_repo.with_new_file(absolute_path_to_new_metadata, new_metadata)
