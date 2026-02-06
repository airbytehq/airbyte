"""Validation script for 1Password migration."""

import subprocess
import json
from dataclasses import dataclass
from naming_utils import extract_root_name


@dataclass
class ValidationResult:
    connector: str
    valid: bool
    missing_fields: list[str]
    extra_fields: list[str]
    details: str


def get_1password_item(connector_name: str, vault: str) -> dict | None:
    result = subprocess.run(
        ["op", "item", "get", connector_name, "--vault", vault, "--format=json"],
        capture_output=True, text=True,
    )
    return json.loads(result.stdout) if result.returncode == 0 else None


def validate_migration(connector_name: str, gsm_secrets: list[dict],
                       vault: str = "replication-connector-credentials") -> ValidationResult:
    """
    Validate migration by comparing GSM and 1Password auth fields.

    Args:
        connector_name: Full connector name (e.g., "source-stripe")
        gsm_secrets: List of GSM secrets with audit results
        vault: 1Password vault name

    Note:
        Extracts root name (e.g., "stripe") for 1Password item lookup
    """
    # Extract root name for 1Password lookup (source-stripe -> stripe)
    item_name = extract_root_name(connector_name)
    op_item = get_1password_item(item_name, vault)
    if op_item is None:
        return ValidationResult(connector_name, False, [], [], f"Item '{item_name}' not found in vault")

    gsm_auth_fields: set[str] = set()
    for secret in gsm_secrets:
        gsm_auth_fields.update(secret.get("auth_fields", {}).keys())

    op_auth_fields: set[str] = set()
    for field in op_item.get("fields", []):
        section = field.get("section", {}).get("label", "")
        if section.startswith("test-credentials-"):
            op_auth_fields.add(field.get("label", ""))

    missing = gsm_auth_fields - op_auth_fields
    extra = op_auth_fields - gsm_auth_fields

    return ValidationResult(
        connector_name, len(missing) == 0, list(missing), list(extra),
        f"GSM: {len(gsm_auth_fields)}, 1Password: {len(op_auth_fields)}",
    )
