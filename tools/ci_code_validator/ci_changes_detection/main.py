#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from ci_sonar_qube import ROOT_DIR

from ci_common_utils import Logger

# Filenames used to detect whether the dir is a module
LANGUAGE_MODULE_ID_FILE = {
    ".py": "setup.py",
    # TODO: Add ID files for other languages
}

LOGGER = Logger()


def folder_generator(dir_path: Path) -> Path:
    while dir_path and str(dir_path) != dir_path.root and dir_path != dir_path.parent:
        if dir_path.is_dir():
            yield dir_path
        dir_path = dir_path.parent


def find_py_module(changed_path: Path) -> Optional[Path]:
    """All Python connectors have setup.py file into own sortware folders"""
    for dir_path in folder_generator(changed_path):
        setup_py_file = dir_path / "setup.py"
        if setup_py_file.is_file():
            return dir_path
    return None


def find_java_module(changed_path: Path) -> Optional[Path]:
    """All Java connectors have a folder src/main/java into own folders"""
    for dir_path in folder_generator(changed_path):
        required_java_dir = dir_path / "src/main/java"
        if required_java_dir.is_dir():
            return dir_path
    return None


def list_changed_modules(changed_files: List[str]) -> List[Dict[str, str]]:
    """
    changed_filed are the list of files which were modified in current branch.
    E.g. changed_files = ["tools/ci_static_check_reports/__init__.py", "tools/ci_static_check_reports/setup.py", ...]
    """
    module_folders = {}
    for file_path in changed_files:
        if not file_path.startswith("/"):
            file_path = ROOT_DIR / file_path
        else:
            file_path = Path(file_path)
        module_folder = find_py_module(file_path)
        if module_folder:
            module_folders[module_folder] = "py"
            continue
        module_folder = find_java_module(file_path)
        if module_folder:
            module_folders[module_folder] = "java"

    modules = []
    for module_folder, lang in module_folders.items():
        module_folder = str(module_folder)
        if "airbyte-integrations/connectors" not in module_folder:
            # now we need to detect connectors only
            LOGGER.info(f"skip the folder {module_folder}...")
            continue
        parts = module_folder.split("/")
        module_name = "/".join(parts[-2:])
        modules.append({"folder": module_folder, "lang": lang, "module": module_name})
        LOGGER.info(f"Detected the module: {module_name}({lang}) in the folder: {module_folder}")
        # _, file_extension = os.path.splitext(file_path)
        # find_base_path(file_path, modules, file_ext=file_extension, unique_modules=unique_modules)
    return modules


def main() -> int:
    changed_modules = list_changed_modules(sys.argv[1:])
    print(json.dumps(changed_modules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
