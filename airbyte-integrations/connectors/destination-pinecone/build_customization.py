# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Image build customization script."""

from __future__ import annotations

from contextlib import suppress
from types import ModuleType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    dagger: ModuleType | None = None
    with suppress(ImportError):
        from dagger import Container



async def pre_connector_install(base_image_container: Container) -> Container:
    return base_image_container.with_exec(["sh", "-c", "apt-get update && apt-get install -y build-essential gcc"], use_entrypoint=True)


if __name__ == "__main__":
    # If this script is invoked directly, run the steps directly using the subprocess module.
    # This is useful for running the script outside of a Dagger environment.
    import subprocess

    subprocess.run(["sh", "-c", "apt-get update && apt-get install -y build-essential gcc"], check=True)
