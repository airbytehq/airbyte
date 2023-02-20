#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

RUN_BLACK_CMD = ["python", "-m", "black", "--config=/pyproject.toml", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", "--settings-file=/pyproject.toml", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", "--config=/pyproject.toml", "."]


async def check_format(client, connector_builder):
    formatter = (
        connector_builder.with_mounted_file(
            "/pyproject.toml", client.host().directory(".", include=["pyproject.toml"]).file(PYPROJECT_TOML_FILE_PATH)
        )  # TODO more elegant way of mounting a single file from root folder?
        .with_exec(["echo", "Running black"])
        .with_exec(RUN_BLACK_CMD)
        .with_exec(["echo", "Running Isort"])
        .with_exec(RUN_ISORT_CMD)
        .with_exec(["echo", "Running Flake"])
        .with_exec(RUN_FLAKE_CMD)
    )
    return await formatter.exit_code()
