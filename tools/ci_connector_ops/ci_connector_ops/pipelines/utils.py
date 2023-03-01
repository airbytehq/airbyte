#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from enum import Enum
from pathlib import Path
from typing import Optional

from ci_connector_ops.utils import Connector
from dagger import Container, QueryError


class StepStatus(Enum):
    SUCCESS = "🟢"
    FAILURE = "🔴"
    SKIPPED = "🟡"

    def from_exit_code(exit_code: int):
        if exit_code == 0:
            return StepStatus.SUCCESS
        if exit_code == 1:
            return StepStatus.FAILURE

    def __str__(self) -> str:
        return self.value


# This utils will probably be redundant once https://github.com/dagger/dagger/issues/3764 is implemented
async def check_path_in_workdir(container: Container, path: str) -> bool:
    """Check if a local path is mounted to the working directory of a container

    Args:
        container (Container): The container on which we want the check the path existence.
        path (str): Directory or file path we want to check the existence in the container working directory.

    Returns:
        bool: Whether the path exists in the container working directory.
    """
    workdir = (await container.with_exec(["pwd"]).stdout()).strip()
    mounts = await container.mounts()
    if workdir in mounts:
        expected_file_path = Path(workdir[1:]) / path
        return expected_file_path.is_file() or expected_file_path.is_dir()
    else:
        return False


# This utils will probably be redundant once https://github.com/dagger/dagger/issues/3764 is implemented
async def get_file_contents(container: Container, path: str) -> Optional[str]:
    """Retrieve a container file contents.

    Args:
        container (Container): The container hosting the file you want to read.
        path (str): Path, in the container, to the file you want to read.

    Returns:
        Optional[str]: The file content if the file exists in the container, None otherwise.
    """
    try:
        return await container.file(path).contents()
    except QueryError as e:
        if "no such file or directory" not in str(e):
            # this is the hicky bit of the stopgap because
            # this error could come from a network issue
            raise
    return None


def write_connector_secrets_to_local_storage(connector: Connector, gsm_credentials: str):
    """Download and write connector's secrets locally.

    Args:
        connector (Connector): The connector for which you want to download secrets.
        gsm_credentials (str): The credentials to connect to GSM.
    """
    connector_secrets = connector.get_secret_manager(gsm_credentials).read_from_gsm()

    for secret in connector_secrets:
        secret_directory = Path(secret.directory)
        secret_directory.mkdir(parents=True, exist_ok=True)
        filepath = secret_directory / secret.configuration_file_name
        with open(filepath, "w") as file:
            file.write(secret.value)
