#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import os
import sys
from typing import Dict, List, Set

# Filenames used to detect whether the dir is a module
LANGUAGE_MODULE_ID_FILE = {
    ".py": "setup.py",
    # TODO: Add ID files for other languages
}


def find_base_path(path: str, modules: List[Dict[str, str]], unique_modules: Set[str], file_ext: str = "", lookup_file: str = None) -> None:
    filename, file_extension = os.path.splitext(path)
    lookup_file = lookup_file or LANGUAGE_MODULE_ID_FILE.get(file_extension)

    dir_path = os.path.dirname(filename)
    if dir_path and os.path.exists(dir_path):
        is_module_root = lookup_file in os.listdir(dir_path)
        if is_module_root:
            if dir_path not in unique_modules:
                modules.append({"dir": dir_path, "lang": file_ext[1:]})
                unique_modules.add(dir_path)
        else:
            find_base_path(dir_path, modules, unique_modules, file_ext=file_extension, lookup_file=lookup_file)


def list_changed_modules(changed_files: List[str]) -> List[Dict[str, str]]:
    """
    changed_filed are the list of files which were modified in current branch.
    E.g. changed_files = ["tools/ci_static_check_reports/__init__.py", "tools/ci_static_check_reports/setup.py", ...]
    """

    modules: List[Dict[str, str]] = []
    unique_modules: set = set()
    for file_path in changed_files:
        _, file_extension = os.path.splitext(file_path)
        find_base_path(file_path, modules, file_ext=file_extension, unique_modules=unique_modules)
    return modules


def main() -> int:
    changed_modules = list_changed_modules(sys.argv[1:])
    print(json.dumps(changed_modules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
