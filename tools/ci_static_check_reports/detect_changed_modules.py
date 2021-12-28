#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
import sys

# Filenames used to detect whether the dir is a module
from pathlib import Path
from typing import List, Set

LANGUAGE_MODULE_ID_FILE = {
    ".py": "setup.py",
    # TODO: Add ID files for other languages
}


def find_base_path(path: str, modules: Set[str], lookup_file: str = None) -> None:
    filename, file_extension = os.path.splitext(path)
    lookup_file = lookup_file or LANGUAGE_MODULE_ID_FILE.get(file_extension)

    dir_path = os.path.dirname(filename)
    if dir_path and os.path.exists(dir_path):
        is_module_root = lookup_file in os.listdir(dir_path)
        if is_module_root:
            modules.add(dir_path)
        else:
            find_base_path(dir_path, modules, lookup_file=lookup_file)


def list_changed_modules(changed_files: List[str]) -> Set[str]:
    os.chdir(Path(__file__).parents[2])
    modules: set = set()
    for file_path in changed_files:
        find_base_path(file_path, modules)
    return modules


if __name__ == "__main__":
    changed_modules = list_changed_modules(sys.argv[1:])
    print(" ".join(changed_modules))
