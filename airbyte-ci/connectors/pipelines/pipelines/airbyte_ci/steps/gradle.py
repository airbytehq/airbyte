#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import shutil
import signal
import subprocess
from abc import ABC
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, Generator, List, Optional, Tuple, cast

from dagger import Container, ExecError

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.utils import dagger_directory_as_zip_file
from pipelines.models.artifacts import Artifact
from pipelines.models.secrets import Secret
from pipelines.models.steps import Step, StepResult, StepStatus


class InvalidGradleEnvironment(Exception):
    pass


class GradleTimeoutError(Exception):
    """Raised when a Gradle operation times out."""

    pass


class GradleExecutionError(Exception):
    """Raised when a Gradle execution fails due to an unexpected error."""

    pass


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        title (str): The step title.
        gradle_task_name (str): The Gradle task name to run.
        bind_to_docker_host (bool): Whether to install the docker client and bind it to the host.
        mount_connector_secrets (bool): Whether to mount connector secrets.
    """

    context: ConnectorContext

    STATIC_GRADLE_OPTIONS = ("--build-cache", "--scan", "--no-watch-fs")
    gradle_task_name: ClassVar[str]

    with_test_artifacts: ClassVar[bool] = False
    accept_extra_params = True

    GRADLE_TIMEOUT = 3600 * 2  # 2 hour timeout by default

    @property
    def gradle_task_options(self) -> Tuple[str, ...]:
        if self.context.s3_build_cache_access_key_id and self.context.s3_build_cache_secret_key:
            return self.STATIC_GRADLE_OPTIONS + (f"-Ds3BuildCachePrefix={self.context.connector.technical_name}",)
        return self.STATIC_GRADLE_OPTIONS

    def _get_gradle_command(self, task: str, *args: Any, task_options: Optional[List[str]] = None) -> str:
        task_options = task_options or []
        return f"./gradlew {' '.join(self.gradle_task_options + args)} {task} {' '.join(task_options)}"

    def check_system_requirements(self) -> None:
        """
        Check if the system has all the required commands in the path.
        This could be improved to check for more specific versions of the commands.
        """
        required_commands_in_path = ["docker", "gradle", "jq", "xargs", "java"]
        for command in required_commands_in_path:
            if not shutil.which(command):
                raise ValueError(f"Command {command} is not in the path")

    @property
    def gradle_command(self) -> str:
        connector_gradle_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
        return self._get_gradle_command(connector_gradle_task, task_options=self.params_as_cli_options)

    def timeout_handler(self, signum: int, frame: Any) -> None:
        raise GradleTimeoutError(f"Gradle operation timed out after {self.GRADLE_TIMEOUT} seconds")

    @contextmanager
    def gradle_environment(self) -> Generator[None, None, None]:
        """
        Context manager to set the gradle environment with timeout:
        - Check if the system has all the required commands in the path.
        - Set the S3 build cache environment variables if available.
        - Enforces a timeout for gradle operations
        - ... Add whatever setup/teardown logic needed to run a gradle task.

        Raises:
            InvalidGradleEnvironment: If the gradle environment is not properly set up
            GradleTimeoutError: If the gradle operation exceeds the timeout
        """

        def set_env_vars() -> Dict[str, str]:
            # Set the RUN_IN_AIRBYTE_CI environment variable to True to tell gradle to use the docker image that was previously built in the airbyte-ci pipeline
            env_vars = {"RUN_IN_AIRBYTE_CI": "True"}

            # Set the S3 build cache environment variables if available.
            if self.context.s3_build_cache_access_key_id and self.context.s3_build_cache_secret_key:
                env_vars["S3_BUILD_CACHE_ACCESS_KEY_ID"] = self.context.s3_build_cache_access_key_id.value
                env_vars["S3_BUILD_CACHE_SECRET_KEY"] = self.context.s3_build_cache_secret_key.value

            for key, value in env_vars.items():
                os.environ[key] = value
            return env_vars

        def unset_env_vars(env_vars: Dict[str, str]) -> None:
            for key in env_vars.keys():
                del os.environ[key]

        def write_secrets(secrets: List[Secret]) -> List[Path]:
            secrets_paths = []
            secrets_dir = f"{self.context.connector.code_directory}/secrets"
            for secret in secrets:
                secret_path = Path(f"{secrets_dir}/{secret.file_name}")
                secret_path.parent.mkdir(parents=True, exist_ok=True)
                secret_path.write_text(secret.value)
                secrets_paths.append(secret_path)
            return secrets_paths

        def remove_secrets(secrets_paths: List[Path]) -> None:
            for secret_path in secrets_paths:
                secret_path.unlink()

        # Set the timeout handler for gradle operations
        original_timeout_handler = signal.signal(signal.SIGALRM, self.timeout_handler)

        try:
            # Check if the system has all the required commands in the path.
            self.check_system_requirements()
            # Set env vars and write secrets - will be undone in the finally block
            env_vars = set_env_vars()
            secret_paths = write_secrets(self.secrets)

            # Set the timeout for gradle operations via SIGALRM
            self.logger.info(f"Setting gradle timeout to {self.GRADLE_TIMEOUT} seconds")
            signal.alarm(self.GRADLE_TIMEOUT)

            yield None
        except GradleTimeoutError:
            raise
        except InvalidGradleEnvironment:
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions in GradleExecutionError
            raise GradleExecutionError(f"Unexpected error during gradle execution: {str(e)}") from e
        finally:
            signal.alarm(0)  # Disable the alarm
            signal.signal(signal.SIGALRM, original_timeout_handler)  # Restore original handler
            unset_env_vars(env_vars)
            # Remove secrets from the secrets folders only in CI
            if self.context.is_ci:
                remove_secrets(secret_paths)

    def _run_gradle_in_subprocess(self) -> Tuple[str, str, int]:
        """
        Run a gradle command in a subprocess.
        """
        try:
            self.context.logger.info(f"Running gradle command: {self.gradle_command}")
            process = subprocess.Popen(
                self.gradle_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                stderr = f"Error while running gradle command: {self.gradle_command}\n{stderr}"
                return stdout, stderr, process.returncode

            return stdout, stderr, process.returncode
        finally:
            # Ensure process is terminated if something goes wrong
            if "process" in locals():
                self.logger.info("Terminating gradle process")
                process.terminate()
                process.wait(timeout=20)  # Give it 20 seconds to terminate gracefully
                try:
                    self.logger.info("Force killing gradle process")
                    process.kill()
                except ProcessLookupError:
                    pass

    async def _run(self, *args: Any, **kwargs: Any) -> StepResult:
        try:
            with self.gradle_environment():
                stdout, stderr, returncode = self._run_gradle_in_subprocess()
                artifacts = []
                if self.with_test_artifacts:
                    if test_logs := await self._collect_test_logs():
                        artifacts.append(test_logs)
                    if test_results := await self._collect_test_results():
                        artifacts.append(test_results)
                step_result = StepResult(
                    step=self,
                    status=StepStatus.SUCCESS if returncode == 0 else StepStatus.FAILURE,
                    stdout=stdout,
                    stderr=stderr,
                    output=self.context.dagger_client.host().directory(str(self.context.connector.code_directory)),
                    artifacts=artifacts,
                )
                return step_result
        except GradleTimeoutError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )
        except InvalidGradleEnvironment as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )

    async def _collect_test_logs(self) -> Optional[Artifact]:
        """
        Exports the java docs to the host filesystem as a zip file.
        The docs are expected to be in build/test-logs, and will end up test-artifact directory by default
        One can change the destination directory by setting the outputs
        """
        test_logs_dir_name_in_container = "test-logs"
        test_logs_dir_name_in_zip = f"test-logs-{datetime.fromtimestamp(cast(float, self.context.pipeline_start_timestamp)).isoformat()}-{self.context.git_branch}-{self.gradle_task_name}".replace(
            "/", "_"
        )
        if (
            test_logs_dir_name_in_container
            not in await self.dagger_client.host().directory(f"{self.context.connector.code_directory}/build").entries()
        ):
            self.context.logger.warn(f"No {test_logs_dir_name_in_container} found directory in the build folder")
            return None
        try:
            zip_file = await dagger_directory_as_zip_file(
                self.dagger_client,
                await self.dagger_client.host().directory(
                    f"{self.context.connector.code_directory}/build/{test_logs_dir_name_in_container}"
                ),
                test_logs_dir_name_in_zip,
            )
            return Artifact(
                name=f"{test_logs_dir_name_in_zip}.zip",
                content=zip_file,
                content_type="application/zip",
                to_upload=True,
            )
        except ExecError as e:
            self.context.logger.error(str(e))
        return None

    async def _collect_test_results(self) -> Optional[Artifact]:
        """
        Exports the junit test results into the host filesystem as a zip file.
        The docs in the container are expected to be in build/test-results, and will end up test-artifact directory by default
        Only the XML files generated by junit are downloaded into the host filesystem
        One can change the destination directory by setting the outputs
        """
        test_results_dir_name_in_container = "test-results"
        test_results_dir_name_in_zip = f"test-results-{datetime.fromtimestamp(cast(float, self.context.pipeline_start_timestamp)).isoformat()}-{self.context.git_branch}-{self.gradle_task_name}".replace(
            "/", "_"
        )
        if (
            test_results_dir_name_in_container
            not in await self.dagger_client.host().directory(f"{self.context.connector.code_directory}/build").entries()
        ):
            self.context.logger.warn(f"No {test_results_dir_name_in_container} found directory in the build folder")
            return None
        try:
            zip_file = await dagger_directory_as_zip_file(
                self.dagger_client,
                await self.dagger_client.host().directory(
                    f"{self.context.connector.code_directory}/build/{test_results_dir_name_in_container}"
                ),
                test_results_dir_name_in_zip,
            )
            return Artifact(
                name=f"{test_results_dir_name_in_zip}.zip",
                content=zip_file,
                content_type="application/zip",
                to_upload=True,
            )
        except ExecError as e:
            self.context.logger.error(str(e))
            return None
