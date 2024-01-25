#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

import dagger
from pipelines.helpers.docker import get_image_name_with_registry_index


async def list_files_in_directory(dagger_client: dagger.Client, directory: dagger.Directory) -> List[str]:
    """
    List all files in a directory.
    """
    return (
        await dagger_client.container()
        .from_(get_image_name_with_registry_index("bash:latest"))
        .with_mounted_directory("/to_list", directory)
        .with_workdir("/to_list")
        .with_exec(["find", ".", "-type", "f"])
        .stdout()
    ).splitlines()
