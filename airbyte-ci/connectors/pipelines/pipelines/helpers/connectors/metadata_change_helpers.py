#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import yaml  # type: ignore
from dagger import Directory

# Helpers


async def get_current_metadata(repo_dir: Directory, metadata_path: Path) -> dict:
    return yaml.safe_load(await repo_dir.file(str(metadata_path)).contents())


async def get_current_metadata_str(repo_dir: Directory, metadata_path: Path) -> str:
    return await repo_dir.file(str(metadata_path)).contents()


def get_repo_dir_with_updated_metadata(repo_dir: Directory, metadata_path: Path, updated_metadata: dict) -> Directory:
    return repo_dir.with_new_file(str(metadata_path), contents=yaml.safe_dump(updated_metadata))


def get_repo_dir_with_updated_metadata_str(repo_dir: Directory, metadata_path: Path, updated_metadata_str: str) -> Directory:
    return repo_dir.with_new_file(str(metadata_path), contents=updated_metadata_str)


def get_current_version(current_metadata: dict) -> str:
    return current_metadata.get("data", {}).get("dockerImageTag")
