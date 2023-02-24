#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.ci.actions.connector_builder import PYPROJECT_TOML_FILE_PATH, connector_has_path

RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "."]


async def build(client, local_src, tag):
    connector_container = client.host().directory(local_src, exclude=[".venv"]).docker_build()
    return await connector_container.publish(tag)
