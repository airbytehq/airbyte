# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import io
from pathlib import Path
from typing import List

from dagger import Directory
from ruamel.yaml import YAML  # type: ignore


def read_yaml(file_path: Path) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    return yaml.load(file_path)


async def read_dagger_yaml(dir: Directory, file_path: Path) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    contents = await dir.file(str(file_path)).contents()
    return yaml.load(contents)


def write_dagger_yaml(dir: Directory, input: dict | List, file_path: Path) -> Directory:
    data = copy.deepcopy(input)
    yaml = YAML()
    buffer = io.BytesIO()
    yaml.dump(data, buffer)
    new_content = buffer.getvalue().decode("utf-8")
    dir = dir.with_new_file(str(file_path), contents=new_content)
    return dir


def write_yaml(input: dict | List, file_path: Path) -> None:
    data = copy.deepcopy(input)
    yaml = YAML()
    buffer = io.BytesIO()
    yaml.dump(data, buffer)
    with file_path.open("w") as file:
        file.write(buffer.getvalue().decode("utf-8"))
