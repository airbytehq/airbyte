#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import datetime
import json
import logging
import os
import subprocess
import uuid
from pathlib import Path

import anyio
import asyncer
import dagger

from live_tests.commons import errors
from live_tests.commons.models import Command, ExecutionInputs, ExecutionResult
from live_tests.commons.proxy import Proxy


class ConnectorRunner:
    DATA_DIR = "/airbyte/data"
    IN_CONTAINER_CONFIG_PATH = f"{DATA_DIR}/config.json"
    IN_CONTAINER_CONFIGURED_CATALOG_PATH = f"{DATA_DIR}/catalog.json"
    IN_CONTAINER_STATE_PATH = f"{DATA_DIR}/state.json"
    IN_CONTAINER_OUTPUT_PATH = f"{DATA_DIR}/output.txt"
    IN_CONTAINER_OBFUSCATOR_PATH = "/user/local/bin/record_obfuscator.py"

    def __init__(
        self,
        dagger_client: dagger.Client,
        execution_inputs: ExecutionInputs,
        is_airbyte_ci: bool,
        http_proxy: Proxy | None = None,
    ):
        self.connector_under_test = execution_inputs.connector_under_test
        self.command = execution_inputs.command
        self.output_dir = execution_inputs.output_dir
        self.config = execution_inputs.config
        self.configured_catalog = execution_inputs.configured_catalog
        self.state = execution_inputs.state
        self.duckdb_path = execution_inputs.duckdb_path
        self.actor_id = execution_inputs.actor_id
        self.hashed_connection_id = execution_inputs.hashed_connection_id
        self.environment_variables = execution_inputs.environment_variables if execution_inputs.environment_variables else {}

        self.full_command: list[str] = self._get_full_command(execution_inputs.command)
        self.completion_event = anyio.Event()
        self.http_proxy = http_proxy
        self.logger = logging.getLogger(f"{self.connector_under_test.name}-{self.connector_under_test.version}")
        self.dagger_client = dagger_client
        if is_airbyte_ci:
            self.host_obfuscator_path = "/tmp/record_obfuscator.py"
        else:
            repo_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode())
            self.host_obfuscator_path = f"{repo_root}/tools/bin/record_obfuscator.py"

    @property
    def _connector_under_test_container(self) -> dagger.Container:
        return self.connector_under_test.container

    @property
    def stdout_file_path(self) -> Path:
        return (self.output_dir / "stdout.log").resolve()

    @property
    def stderr_file_path(self) -> Path:
        return (self.output_dir / "stderr.log").resolve()

    def _get_full_command(self, command: Command) -> list[str]:
        """Returns a list with a full Airbyte command invocation and all it's arguments and options."""
        if command is Command.SPEC:
            return ["spec"]
        elif command is Command.CHECK:
            return ["check", "--config", self.IN_CONTAINER_CONFIG_PATH]
        elif command is Command.DISCOVER:
            return ["discover", "--config", self.IN_CONTAINER_CONFIG_PATH]
        elif command is Command.READ:
            return [
                "read",
                "--config",
                self.IN_CONTAINER_CONFIG_PATH,
                "--catalog",
                self.IN_CONTAINER_CONFIGURED_CATALOG_PATH,
            ]
        elif command is Command.READ_WITH_STATE:
            return [
                "read",
                "--config",
                self.IN_CONTAINER_CONFIG_PATH,
                "--catalog",
                self.IN_CONTAINER_CONFIGURED_CATALOG_PATH,
                "--state",
                self.IN_CONTAINER_STATE_PATH,
            ]
        else:
            raise NotImplementedError(f"The connector runner does not support the {command} command")

    async def get_container_env_variable_value(self, name: str) -> str | None:
        return await self._connector_under_test_container.env_variable(name)

    async def get_container_label(self, label: str) -> str | None:
        return await self._connector_under_test_container.label(label)

    async def get_container_entrypoint(self) -> str:
        entrypoint = await self._connector_under_test_container.entrypoint()
        assert entrypoint, "The connector container has no entrypoint"
        return " ".join(entrypoint)

    async def run(self) -> ExecutionResult:
        async with asyncer.create_task_group() as task_group:
            soon_result = task_group.soonify(self._run)()
            task_group.soonify(self._log_progress)()
        return soon_result.value

    async def _run(
        self,
    ) -> ExecutionResult:
        container = self._connector_under_test_container
        current_user = (await container.with_exec(["whoami"]).stdout()).strip()
        container = container.with_user(current_user)
        container = container.with_exec(["mkdir", "-p", self.DATA_DIR])
        # Do not cache downstream dagger layers
        container = container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))

        # When running locally, it's likely that record_obfuscator is within the user's home directory, so we expand it.
        expanded_host_executable_path = os.path.expanduser(self.host_obfuscator_path)
        container = container.with_file(
            self.IN_CONTAINER_OBFUSCATOR_PATH,
            self.dagger_client.host().file(expanded_host_executable_path),
        )

        for env_var_name, env_var_value in self.environment_variables.items():
            container = container.with_env_variable(env_var_name, env_var_value)
        if self.config:
            container = container.with_new_file(self.IN_CONTAINER_CONFIG_PATH, contents=json.dumps(dict(self.config)), owner=current_user)
        if self.state:
            container = container.with_new_file(self.IN_CONTAINER_STATE_PATH, contents=json.dumps(self.state), owner=current_user)
        if self.configured_catalog:
            container = container.with_new_file(
                self.IN_CONTAINER_CONFIGURED_CATALOG_PATH,
                contents=self.configured_catalog.json(),
                owner=current_user,
            )
        if self.http_proxy:
            container = await self.http_proxy.bind_container(container)

        self.logger.info(f"⏳ Start running {self.command.value} command")

        try:
            entrypoint = await container.entrypoint()
            assert entrypoint, "The connector container has no entrypoint"
            airbyte_command = entrypoint + self.full_command

            container = container.with_exec(
                [
                    "sh",
                    "-c",
                    " ".join(airbyte_command)
                    + f"| {self.IN_CONTAINER_OBFUSCATOR_PATH} > {self.IN_CONTAINER_OUTPUT_PATH} 2>&1 | tee -a {self.IN_CONTAINER_OUTPUT_PATH}",
                ]
            )
            executed_container = await container.sync()
            # We exporting to disk as we can't read .stdout() or await file.contents() as it might blow up the memory
            stdout_exported = await executed_container.file(self.IN_CONTAINER_OUTPUT_PATH).export(str(self.stdout_file_path))
            if not stdout_exported:
                raise errors.ExportError(f"Failed to export {self.IN_CONTAINER_OUTPUT_PATH}")

            stderr = await executed_container.stderr()
            self.stderr_file_path.write_text(stderr)
            success = True
        except dagger.ExecError as e:
            self.stderr_file_path.write_text(e.stderr)
            self.stdout_file_path.write_text(e.stdout)
            executed_container = None
            success = False

        self.completion_event.set()
        if not success:
            self.logger.error(f"❌ Failed to run {self.command.value} command")
        else:
            self.logger.info(f"⌛ Finished running {self.command.value} command")

        execution_result = await ExecutionResult.load(
            command=self.command,
            connector_under_test=self.connector_under_test,
            actor_id=self.actor_id,
            hashed_connection_id=self.hashed_connection_id,
            configured_catalog=self.configured_catalog,
            stdout_file_path=self.stdout_file_path,
            stderr_file_path=self.stderr_file_path,
            success=success,
            http_dump=await self.http_proxy.retrieve_http_dump() if self.http_proxy else None,
            executed_container=executed_container,
            config=self.config,
        )
        await execution_result.save_artifacts(self.output_dir, self.duckdb_path)
        return execution_result

    async def _log_progress(self) -> None:
        start_time = datetime.datetime.utcnow()
        message = f"⏳ Still running {self.command.value} command"
        while not self.completion_event.is_set():
            duration = datetime.datetime.utcnow() - start_time
            elapsed_seconds = duration.total_seconds()
            if elapsed_seconds > 10 and round(elapsed_seconds) % 10 == 0:
                self.logger.info(f"{message} (duration: {self.format_duration(duration)})")
            await anyio.sleep(1)

    @staticmethod
    def format_duration(time_delta: datetime.timedelta) -> str:
        total_seconds = time_delta.total_seconds()
        if total_seconds < 60:
            return f"{total_seconds:.2f}s"
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}mn{seconds:02d}s"
