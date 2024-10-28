# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import subprocess
from pathlib import Path
from typing import List

from pipelines.cli.ensure_repo_root import get_airbyte_repo_path_with_fallback


async def format_prettier(files: List[Path], logger: logging.Logger) -> None:
    if len(files) == 0:
        return

    repo_root_path = get_airbyte_repo_path_with_fallback()
    config_path = repo_root_path / ".prettierrc"
    if not config_path.exists():
        raise Exception(f"Prettier config file not found: {config_path}")

    to_format = [str(file) for file in files]

    logger.info(f"       Formatting files: npx prettier --write {' '.join(to_format)}")
    command = ["npx", "prettier", "--config", str(config_path), "--write"] + to_format
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("        Files formatted successfully.")
    else:
        logger.warn("        Error formatting files.")


def verify_formatters() -> None:
    try:
        subprocess.run(["npx", "--version"], check=True)
    except subprocess.CalledProcessError:
        raise Exception("npx is required to format files. Please install Node.js and npm.")
