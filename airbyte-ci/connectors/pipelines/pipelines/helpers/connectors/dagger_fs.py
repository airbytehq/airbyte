# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path

from dagger import Directory, QueryError


# TODO: sometimes we have the full path (connector.metadata_file_path) but we want to be using just the connector dir
# so we could pass in a subdir here:
# await file_exists(connector_dir, connector.metadata_file_path, relative_to=connector.code_directory)
async def dagger_file_exists(dir: Directory, path: Path | str) -> bool:
    try:
        await dir.file(str(path))
        return True
    except QueryError:
        return False


async def dagger_read_file(directory: Directory, path: Path | str) -> str:
    if str(path) not in await directory.entries():
        raise FileNotFoundError(f"File {path} not found in directory {directory}")
    content = await directory.file(str(path)).contents()
    return content


def dagger_write_file(directory: Directory, path: Path | str, new_content: str) -> Directory:
    directory = directory.with_new_file(str(path), contents=new_content)
    return directory


async def dagger_export_file(dir: Directory, path: Path | str) -> bool:
    success = await dir.file(str(path)).export(str(path))
    return success


async def dagger_dir_exists(dir: Directory, path: Path | str) -> bool:
    try:
        await dir.directory(str(path))
        return True
    except QueryError:
        return False
