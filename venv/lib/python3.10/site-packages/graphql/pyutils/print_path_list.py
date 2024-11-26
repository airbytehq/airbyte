from typing import Collection, Union


def print_path_list(path: Collection[Union[str, int]]) -> str:
    """Build a string describing the path."""
    return "".join(f"[{key}]" if isinstance(key, int) else f".{key}" for key in path)
