#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

from dagger.api.gen import Container


async def check_path_in_workdir(container: Container, path: str):
    workdir = (await container.with_exec(["pwd"]).stdout()).strip()
    mounts = await container.mounts()
    if workdir in mounts:
        expected_file_path = Path(workdir[1:]) / path
        return expected_file_path.is_file() or expected_file_path.is_dir()
    else:
        return False
