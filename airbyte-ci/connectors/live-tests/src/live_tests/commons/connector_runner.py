#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import datetime
import json
import logging
import uuid
from pathlib import Path
from typing import Optional

import anyio
import asyncer
import dagger
from live_tests.commons import errors
from live_tests.commons.models import Command, ExecutionInputs, ExecutionResult
from live_tests.commons.proxy import Proxy


class ConnectorRunner:
    IN_CONTAINER_CONFIG_PATH = "/data/config.json"
    IN_CONTAINER_CONFIGURED_CATALOG_PATH = "/data/catalog.json"
    IN_CONTAINER_STATE_PATH = "/data/state.json"
    IN_CONTAINER_OUTPUT_PATH = "/output.txt"

    def __init__(
        self,
        dagger_client: dagger.Client,
        execution_inputs: ExecutionInputs,
        http_proxy: Optional[Proxy] = None,
    ):
        self.connector_under_test = execution_inputs.connector_under_test
        self.command = execution_inputs.command
        self.output_dir = execution_inputs.output_dir
        self.config = execution_inputs.config
        self.configured_catalog = execution_inputs.configured_catalog
        self.state = execution_inputs.state
        self.duckdb_path = execution_inputs.duckdb_path
        self.actor_id = execution_inputs.actor_id
        self.environment_variables = execution_inputs.environment_variables if execution_inputs.environment_variables else {}

        self.full_command: list[str] = self._get_full_command(execution_inputs.command)
        self.completion_event = anyio.Event()
        self.http_proxy = http_proxy
        self.logger = logging.getLogger(f"{self.connector_under_test.name}-{self.connector_under_test.version}")
        self.dagger_client = dagger_client.pipeline(f"{self.connector_under_test.name}-{self.connector_under_test.version}")

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

    async def get_container_env_variable_value(self, name: str) -> Optional[str]:
        return await self._connector_under_test_container.env_variable(name)

    async def get_container_label(self, label: str) -> Optional[str]:
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
        # Do not cache downstream dagger layers
        container = container.with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
        for env_var_name, env_var_value in self.environment_variables.items():
            container = container.with_env_variable(env_var_name, env_var_value)
        if self.config:
            container = container.with_new_file(self.IN_CONTAINER_CONFIG_PATH, contents=json.dumps(dict(self.config)))
        if self.state:
            container = container.with_new_file(self.IN_CONTAINER_STATE_PATH, contents=json.dumps(self.state))
        if self.configured_catalog:
            container = container.with_new_file(
                self.IN_CONTAINER_CONFIGURED_CATALOG_PATH,
                contents=self.configured_catalog.json(),
            )
        if self.http_proxy:
            container = await self.http_proxy.bind_container(container)

        self.logger.info(f"⏳ Start running {self.command.value} command")

        try:
            entrypoint = await container.entrypoint()
            assert entrypoint, "The connector container has no entrypoint"
            airbyte_command = entrypoint + self.full_command
            # We are piping the output to a file to avoidQueryError: file size exceeds limit 134217728
            container = container.with_exec(
                [
                    "sh",
                    "-c",
                    " ".join(airbyte_command) + f" > {self.IN_CONTAINER_OUTPUT_PATH} 2>&1 | tee -a {self.IN_CONTAINER_OUTPUT_PATH}",
                ],
                skip_entrypoint=True,
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
            stdout_file_path=self.stdout_file_path,
            stderr_file_path=self.stderr_file_path,
            success=success,
            http_dump=await self.http_proxy.retrieve_http_dump() if self.http_proxy else None,
            executed_container=executed_container,
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
