#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import sys
from pathlib import Path
from typing import Dict, List

from ci_common_utils import Logger
from ci_sonar_qube import ROOT_DIR

LOGGER = Logger()

AVAILABLE_SCAN_FOLDERS = (
    "airbyte-integrations/connectors",
    "airbyte-cdk/python",
    "airbyte-integrations/bases/source-acceptance-test",
)


def get_module_folder(dir_path: Path) -> Path:
    while dir_path and str(dir_path) != dir_path.root and dir_path != dir_path.parent:
        parent_path = dir_path.parent
        if dir_path.is_dir():
            for available_folder in AVAILABLE_SCAN_FOLDERS:
                if str(parent_path).endswith(available_folder):
                    """first child of known folder"""
                    return dir_path
        """keep looking up"""
        dir_path = dir_path.parent

    return None


def get_module_type(dir_path: Path) -> Path:
    """All Java connectors have a folder src/main/java into own folders"""
    required_java_dir = dir_path / "src/main/java"
    if required_java_dir.is_dir():
        return "java"

    """All Python connectors have setup.py file into own software folders"""
    setup_py_file = dir_path / "setup.py"
    if setup_py_file.is_file():
        return "py"

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

        module_folder = get_module_folder(file_path)
        if module_folder:
            module_type = get_module_type(module_folder)
            if not module_type:
                LOGGER.info(f"skip the folder {module_folder}...")
            else:
                module_folders[module_folder] = module_type

    modules = []
    for module_folder, lang in module_folders.items():
        module_folder = str(module_folder)
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
