# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import io
from pathlib import Path
from typing import List

from dagger import Directory
from ruamel.yaml import YAML  # type: ignore


def read_yaml(file_path: Path | str) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    return yaml.load(file_path)


async def read_yaml_from_directory(directory: Directory, file_path: str | Path) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    if str(file_path) not in await directory.entries():
        raise FileNotFoundError(f"File {file_path} not found in directory {directory}")
    contents = await directory.file(str(file_path)).contents()
    return yaml.load(contents)


async def write_yaml_to_directory(directory: Directory, yaml_input: dict | List, file_path: str | Path) -> Directory:
    data = copy.deepcopy(yaml_input)
    yaml = YAML()
    buffer = io.BytesIO()
    yaml.dump(data, buffer)
    new_content = buffer.getvalue().decode("utf-8")
    directory = await directory.with_new_file(str(file_path), contents=new_content)
    return directory


def write_yaml(input: dict | List, file_path: str | Path) -> None:
    data = copy.deepcopy(input)
    yaml = YAML()
    buffer = io.BytesIO()
    yaml.dump(data, buffer)
    with open(file_path, "w") as file:
        file.write(buffer.getvalue().decode("utf-8"))
