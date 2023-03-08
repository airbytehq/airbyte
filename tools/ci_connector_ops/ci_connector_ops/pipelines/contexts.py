#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger

from ci_connector_ops.utils import Connector
from dagger import Client, Directory


@dataclass()
class ConnectorTestContext:
    """The connector test context is used to store configuration for a specific connector pipeline run.
    It should only be mutated on setup of the pipeline, not during its run.
    """

    connector: Connector
    is_local: bool
    git_branch: str
    git_revision: str
    use_remote_secrets: bool = True
    # Set default connector_acceptance_test_image to dev as its currently patched in this branch to support Dagger
    connector_acceptance_test_image: str = "airbyte/connector-acceptance-test:dev"
    created_at: datetime = field(default_factory=datetime.utcnow)
    gha_workflow_run_url: str = None

    @property
    def is_ci(self):
        return self.is_local is False

    @property
    def repo(self):
        return self.dagger_client.git("https://github.com/airbytehq/airbyte.git", keep_git_dir=True)

    def get_repo_dir(self, subdir=".", exclude=None, include=None) -> Directory:
        if self.is_local:
            return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)
        else:
            return self.repo.branch(self.git_branch).tree().directory(subdir)

    def get_connector_dir(self, exclude=None, include=None) -> Directory:
        return self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def secrets_dir(self) -> Directory:
        return self._secrets_dir

    @secrets_dir.setter
    def secrets_dir(self, secrets_dir: Directory):
        self._secrets_dir = secrets_dir

    @property
    def updated_secrets_dir(self) -> Directory:
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory):
        self._updated_secrets_dir = updated_secrets_dir

    @property
    def logger(self) -> Logger:
        return self._logger

    @logger.setter
    def logger(self, logger: Logger):
        self._logger = logger

    @property
    def dagger_client(self) -> Logger:
        return self._dagger_client

    @dagger_client.setter
    def dagger_client(self, dagger_client: Client):
        self._dagger_client = dagger_client

    @property
    def should_save_updated_secrets(self):
        return self.use_remote_secrets and self.updated_secrets_dir is not None
