#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


RUN_BLACK_CMD = ["python", "-m", "black", "--config=/pyproject.toml", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", "--settings-file=/pyproject.toml", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", "--config=/pyproject.toml", "."]


async def check_format(connector_builder):
    formatter = (
        connector_builder.with_exec(["echo", "Running black"])
        .with_exec(RUN_BLACK_CMD)
        .with_exec(["echo", "Running Isort"])
        .with_exec(RUN_ISORT_CMD)
        .with_exec(["echo", "Running Flake"])
        .with_exec(RUN_FLAKE_CMD)
    )
    return await formatter.exit_code()
