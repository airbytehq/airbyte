import os
import subprocess
from airbyte_cdk.logger import AirbyteLogger
from pathlib import Path

def run_dbt(*args, project_dir: str, logger: AirbyteLogger, profiles_dir: str = None, **kwargs) -> None:
    dbt_path = "dbt"
    if "dbt_path" in kwargs:
        dbt_path = kwargs.pop("dbt_path")
    profiles_dir = profiles_dir or project_dir

    profiles_dir_path = Path(profiles_dir).absolute()
    project_dir_path = Path(project_dir).absolute()

    arg_list = list(args) + [f"--project-dir={project_dir_path}" ,f"--profiles-dir={profiles_dir_path}"] + [f"--{key}={value}" for key, value in kwargs.items() if value is not None]
    logger.info(f"Running dbt with arguments: {arg_list}")

    # Set NO_COLOR to prevent dbt from printing ANSI color codes
    os.environ["NO_COLOR"] = "true"

    result = subprocess.run([dbt_path, *arg_list], capture_output=True, text=True)
    logger.info(result.stdout)

    if result.returncode != 0:
        logger.info(f'An error occurred. Log: {result.stderr}')
        raise Exception(result.stderr)
