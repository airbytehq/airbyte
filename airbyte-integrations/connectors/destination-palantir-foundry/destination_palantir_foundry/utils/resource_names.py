from typing import Optional


def get_foundry_resource_name(namespace: Optional[str], name: str) -> str:
    if namespace is None:
        return f"[Airbyte] {name}"
    return f"[Airbyte] {namespace} - {name}"
