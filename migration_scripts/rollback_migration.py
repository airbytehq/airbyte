"""Automated rollback for failed migrations."""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from naming_utils import extract_root_name


@dataclass
class RollbackResult:
    connector: str
    success: bool
    actions_taken: list[str]
    error: str | None = None


def rollback_connector(connector_name: str, vault: str = "replication-connector-credentials") -> RollbackResult:
    """
    Rollback a connector migration:
    1. Delete 1Password item
    2. Remove generated config file
    3. Record rollback in log

    Args:
        connector_name: Full connector name (e.g., "source-stripe")
        vault: 1Password vault name

    Note:
        - Extracts root name (e.g., "stripe") for 1Password item deletion
        - Does NOT revert code changes (handled separately by git)
    """
    actions = []

    # Extract root name for 1Password deletion (source-stripe -> stripe)
    item_name = extract_root_name(connector_name)

    # Delete 1Password item
    result = subprocess.run(
        ["op", "item", "delete", item_name, "--vault", vault],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        actions.append(f"Deleted 1Password item: {item_name}")
    else:
        # Item might not exist, continue anyway
        actions.append(f"1Password item '{item_name}' not found (may be already deleted)")

    # Remove config file
    config_file = Path(f"connectors/{connector_name}/defaults.yaml")
    if config_file.exists():
        config_file.unlink()
        actions.append(f"Removed config file: {config_file}")

    # Log rollback
    log_rollback(connector_name, actions)

    return RollbackResult(
        connector=connector_name,
        success=True,
        actions_taken=actions
    )


def log_rollback(connector_name: str, actions: list[str]):
    """Record rollback in migration log."""
    with open("migration_log.jsonl", "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "connector": connector_name,
            "action": "rollback",
            "details": actions
        }) + "\n")
