#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

import dagger
from pipelines.helpers.utils import sh_dash_c


def run_check(
    container: dagger.Container,
    check_commands: List[str],
) -> dagger.Container:
    """Checks whether the repository is formatted correctly.
    Args:
        container: (dagger.Container): The container to run the formatting check in
        check_commands (List[str]): The list of commands to run to check the formatting
    """
    return container.with_exec(sh_dash_c(check_commands), skip_entrypoint=True)


async def run_format(
    container: dagger.Container,
    format_commands: List[str],
) -> dagger.Container:
    """Formats the repository.
    Args:
        container: (dagger.Container): The container to run the formatter in
        format_commands (List[str]): The list of commands to run to format the repository
    """
    format_container = container.with_exec(sh_dash_c(format_commands), skip_entrypoint=True)
    return await format_container.directory("/src").export(".")


def mount_repo_for_formatting(
    dagger_client: dagger.Client,
    container: dagger.Container,
    include: List[str],
) -> dagger.Container:
    """Mounts the relevant parts of the repository: the code to format and the formatting config
    Args:
        container: (dagger.Container): The container to mount the repository in
        include (List[str]): The list of files to include in the container
    """
    container = container.with_mounted_directory(
        "/src",
        dagger_client.host().directory(
            ".",
            include=include,
        ),
    ).with_workdir("/src")

    return container
