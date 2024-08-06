from pathlib import Path as FilePath


def _get_unit_test_folder(execution_folder: str) -> FilePath:
    path = FilePath(execution_folder)
    while path.name != "unit_tests":
        if path.name == path.root or path.name == path.drive:
            raise ValueError(f"Could not find `unit_tests` folder as a parent of {execution_folder}")
        path = path.parent
    return path


def get_json_contents(resource: str, test_location: FilePath) -> str:
    json_path = str(_get_unit_test_folder(test_location) / "resource" / "http" / "response" / f"{resource}")
    with open(json_path) as f:
        response = f.read()
    return response
