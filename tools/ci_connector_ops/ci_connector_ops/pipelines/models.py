#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from logging import Logger
from typing import List, Optional, Union

from ci_connector_ops.utils import Connector
from dagger import Client, Container, Directory


@dataclass()
class ConnectorTestContext:
    connector: Connector
    is_local: bool
    git_branch: str
    git_revision: str
    use_remote_secrets: bool = True
    # Set default connector_acceptance_test_image to dev as its currently patched in this branch to support Dagger
    connector_acceptance_test_image: str = "airbyte/connector-acceptance-test:dev"
    created_at: datetime = field(default_factory=datetime.utcnow)

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


class Step(Enum):
    CODE_FORMAT_CHECKS = "Code format checks"
    PACKAGE_INSTALL = "Package install"
    UNIT_TESTS = "Unit tests"
    INTEGRATION_TESTS = "Integration tests"
    DOCKER_BUILD = "Docker Build"
    ACCEPTANCE_TESTS = "Acceptance tests"
    QA_CHECKS = "QA Checks"

    def get_dagger_pipeline(self, dagger_client_or_container: Union[Client, Container]) -> Union[Client, Container]:
        return dagger_client_or_container.pipeline(self.value)


class StepStatus(Enum):
    SUCCESS = "🟢 — Successful"
    FAILURE = "🔴 - Failed"
    SKIPPED = "🟡 - Skipped"

    def from_exit_code(exit_code: int):
        if exit_code == 0:
            return StepStatus.SUCCESS
        if exit_code == 1:
            return StepStatus.FAILURE
        # pytest returns a 5 exit code when no test is found.
        if exit_code == 5:
            return StepStatus.SKIPPED
        else:
            raise ValueError(f"No step status is mapped to exit code {exit_code}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class StepResult:
    step: Step
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.step.value}: {self.status.value}"


@dataclass(frozen=True)
class ConnectorTestReport:
    connector_test_context: ConnectorTestContext
    steps_results: List[StepResult]
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def failed_steps(self) -> StepResult:
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.FAILURE]

    @property
    def success(self) -> StepResult:
        return len(self.failed_steps) == 0

    @property
    def should_be_saved(self) -> bool:
        return self.connector_test_context.is_ci

    @property
    def run_duration(self) -> int:
        return (self.created_at - self.connector_test_context.created_at).total_seconds()

    def to_json(self) -> str:
        return json.dumps(
            {
                "connector_technical_name": self.connector_test_context.connector.technical_name,
                "connector_version": self.connector_test_context.connector.version,
                "run_timestamp": self.created_at.isoformat(),
                "run_duration": self.run_duration,
                "success": self.success,
                "failed_step": [failed_step_result.step.name for failed_step_result in self.failed_steps],
            }
        )

    def __str__(self) -> str:
        nice_output = f"\n{self.connector_test_context.connector.technical_name.upper()} - TEST RESULTS\n"
        nice_output += "\n".join([str(sr) for sr in self.steps_results]) + "\n"
        nice_output += f"Total duration: {round(self.run_duration)} seconds"
        for failed_step in self.failed_steps:
            nice_output += f"{failed_step.step.value} FAILURES:\n{failed_step.stderr}"
        return nice_output
