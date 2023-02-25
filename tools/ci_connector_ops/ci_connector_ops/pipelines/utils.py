#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from enum import Enum, auto
from pathlib import Path

from dagger.api.gen import Container


class StepStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    SKIPPED = auto()

    def from_exit_code(exit_code: int):
        if exit_code == 0:
            return StepStatus.SUCCESS
        if exit_code == 1:
            return StepStatus.FAILURE

    def __str__(self) -> str:
        if self is StepStatus.SUCCESS:
            return "🟢"
        elif self is StepStatus.FAILURE:
            return "🔴"
        elif self is StepStatus.SKIPPED:
            return "🟡"
        else:
            return super().__str__()


async def check_path_in_workdir(container: Container, path: str):
    workdir = (await container.with_exec(["pwd"]).stdout()).strip()
    mounts = await container.mounts()
    if workdir in mounts:
        expected_file_path = Path(workdir[1:]) / path
        return expected_file_path.is_file() or expected_file_path.is_dir()
    else:
        return False
