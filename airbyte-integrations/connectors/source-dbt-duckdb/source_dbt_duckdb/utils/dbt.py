import os
from airbyte_cdk.logger import AirbyteLogger
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest


def get_dbt_manifest(
    *,
    project_dir: str,
    logger: AirbyteLogger,
    profiles_dir: str = None,
    env_vars: dict[str, str] = None,
) -> Manifest:
    # use 'parse' command to load a Manifest
    dbt_runner_result: dbtRunnerResult = invoke_dbt(
        "parse",
        project_dir=project_dir,
        logger=logger,
        profiles_dir=profiles_dir,
        env_vars=env_vars,
    )
    return dbt_runner_result.result


def invoke_dbt(
    command: str = "run",
    *,
    project_dir: str,
    logger: AirbyteLogger,
    profiles_dir: str = None,
    env_vars: dict[str, str] = None,
    manifest: Manifest = None,
    **kwargs,
) -> dbtRunnerResult:
    profiles_dir = profiles_dir or project_dir

    profiles_dir_path = Path(profiles_dir).absolute()
    project_dir_path = Path(project_dir).absolute()

    arg_list = [
        command,
        f"--project-dir={project_dir_path}",
        f"--profiles-dir={profiles_dir_path}",
    ] + [f"--{key}={value}" for key, value in kwargs.items() if value is not None]
    logger.info(f"Running dbt with arguments: {arg_list}")

    # Set NO_COLOR to prevent dbt from printing ANSI color codes
    os.environ["NO_COLOR"] = "true"

    env_vars = {
        "DUCKDB_DB_DIR": "/Users/ajsteers/Source/airbyte/airbyte-integrations/connectors/source-dbt-duckdb/unit_tests/artifacts",
    }

    os.environ.update(env_vars)

    dbt = dbtRunner(manifest=manifest)
    dbt_runner_result: dbtRunnerResult = dbt.invoke(arg_list)

    if not dbt_runner_result.success:
        logger.info(f"An error occurred. Log: {dbt_runner_result.exception}")
        raise dbt_runner_result.exception

    if command in ["run"]:
        for r in dbt_runner_result.result:
            logger.info(f"dbt result for '{r.node.name}': {r.status}")

    return dbt_runner_result
