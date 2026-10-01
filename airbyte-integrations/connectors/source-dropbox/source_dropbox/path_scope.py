from __future__ import annotations


def in_configured_scope(path_lower: object, root: object) -> bool:
    """Return whether a Dropbox lowercase path is safely inside a configured root."""
    if not isinstance(path_lower, str) or not path_lower:
        return False
    if not isinstance(root, str) or root == "":
        return True
    normalized_root = root.rstrip("/").casefold()
    normalized_path = path_lower.casefold()
    return normalized_path == normalized_root or normalized_path.startswith(f"{normalized_root}/")
