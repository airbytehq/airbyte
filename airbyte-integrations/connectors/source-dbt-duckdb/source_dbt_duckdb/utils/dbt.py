import os
import subprocess
from airbyte_cdk.logger import AirbyteLogger
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult

# initialize
dbt = dbtRunner()


def run_dbt(
    *args,
    project_dir: str,
    logger: AirbyteLogger,
    profiles_dir: str = None,
    env_vars: dict[str, str] = None,
    **kwargs,
) -> None:
    profiles_dir = profiles_dir or project_dir

    profiles_dir_path = Path(profiles_dir).absolute()
    project_dir_path = Path(project_dir).absolute()

    arg_list = list(args) + [f"--project-dir={project_dir_path}" ,f"--profiles-dir={profiles_dir_path}"] + [f"--{key}={value}" for key, value in kwargs.items() if value is not None]
    logger.info(f"Running dbt with arguments: {arg_list}")

    # Set NO_COLOR to prevent dbt from printing ANSI color codes
    os.environ["NO_COLOR"] = "true"

    env_vars = {
        "DUCKDB_DB_DIR": "/Users/ajsteers/Source/airbyte/airbyte-integrations/connectors/source-dbt-duckdb/unit_tests/artifacts",
    }

    os.environ.update(env_vars)
    results_obj: dbtRunnerResult = dbt.invoke(arg_list)

    if not results_obj.success:
        logger.info(f'An error occurred. Log: {results_obj.exception}')
        raise results_obj.exception

    for r in results_obj.result:
        logger.info(f"dbt result for '{r.node.name}': {r.status}")
