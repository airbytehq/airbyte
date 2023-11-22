# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path
from typing import Iterable

from airbyte_cdk.logger import AirbyteLogger
from dbt.cli.main import dbtRunner, dbtRunnerResult, RunExecutionResult

from dbt.contracts.graph.manifest import Manifest
from dbt.cli.main import CatalogArtifact
from dataclasses import dataclass

@dataclass
class AirbyteDbtRunner():
    project_dir: str
    env_vars: dict[str, str]
    logger: AirbyteLogger
    profiles_dir: str | None = None
    manifest: Manifest | None = None

    class Config:
        arbitrary_types_allowed = True

    def generate_manifest(
        self,
    ) -> Manifest:
        dbt_runner_result = self.invoke("parse")
        self.manifest = dbt_runner_result.result
        return self.manifest

    def generate_docs(
        self,
    ) -> CatalogArtifact:
        dbt_runner_result = self.invoke("docs generate")
        return dbt_runner_result.result

    def invoke(
        self,
        command: str = "run",
        **kwargs,
    ) -> dbtRunnerResult:
        profiles_dir = self.profiles_dir or self.project_dir

        profiles_dir_path = Path(profiles_dir).absolute()
        project_dir_path = Path(self.project_dir).absolute()

        arg_list = command.split(" ") + [
            f"--project-dir={project_dir_path}",
            f"--profiles-dir={profiles_dir_path}",
        ] + [f"--{key}={value}" for key, value in kwargs.items() if value is not None]
        self.logger.info(f"Running dbt with arguments: {arg_list}")

        # Set NO_COLOR to prevent dbt from printing ANSI color codes
        os.environ["NO_COLOR"] = "true"

        env_vars = self.env_vars or {}

        os.environ.update(env_vars)

        dbt = dbtRunner(manifest=self.manifest)
        dbt_runner_result: dbtRunnerResult = dbt.invoke(arg_list)

        if not dbt_runner_result.success:
            self.logger.info(f"An error occurred. Log: {dbt_runner_result.exception}")
            raise dbt_runner_result.exception

        if command in ["run"]:
            for r in dbt_runner_result.result:
                self.logger.info(f"dbt result for '{r.node.name}': {r.status}")

        return dbt_runner_result


    def run_with_results(
        self,
        command: str,
    ) -> Iterable[RunExecutionResult]:
        dbt_runner_result = self.invoke(command)
        yield from dbt_runner_result.result
