"""Execute full migration for a connector."""

from pathlib import Path
import yaml
import json
from field_classifier import FieldClassifier
from gsm_audit import audit_connector
from generate_config_defaults import generate_config_file
from gsm_to_1password import OnePasswordMigrator
from validate_migration import validate_migration


def load_json(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)


def load_yaml(filepath: str) -> dict:
    with open(filepath) as f:
        return yaml.safe_load(f)


def load_allowlist() -> set:
    """Load the CONFIG_ALLOWLIST from Phase 1a analysis."""
    data = load_json("phase1a_allowlist.json")
    return set(data["suggested_allowlist"])


def migrate_connector_full(connector_name: str, gsm_credentials: dict, dry_run: bool = True):
    """
    Complete migration workflow:
    1. Audit and classify fields
    2. Generate config defaults file
    3. Migrate secrets to 1Password
    4. Validate migration
    """
    # Phase 1: Audit
    classifier = FieldClassifier()
    classifier.CONFIG_ALLOWLIST = load_allowlist()
    overrides = load_yaml("classification_overrides.yaml")

    audit_result = audit_connector(connector_name, gsm_credentials, classifier, overrides)

    if not audit_result["migration_ready"]:
        print(f"❌ {connector_name} not ready: {audit_result['blocked_reason']}")
        return False

    # Phase 2: Generate config file
    output_dir = Path(f"connectors/{connector_name}")
    generate_config_file(connector_name, audit_result, output_dir)

    # Phase 3: Migrate to 1Password
    migrator = OnePasswordMigrator(dry_run=dry_run)

    # Add variant info to secrets
    for secret in audit_result["secrets"]:
        secret["variant"] = migrator._infer_variant(secret)

    migration_result = migrator.migrate_connector(connector_name, audit_result["secrets"])

    if migration_result.status == "failed":
        print(f"❌ Migration failed: {migration_result.error}")
        return False

    print(f"✓ {migration_result.status}: {migration_result.fields_migrated} fields")

    # Phase 4: Validate
    validation_result = validate_migration(connector_name, audit_result["secrets"])

    if not validation_result.valid:
        print(f"❌ Validation failed: {validation_result.details}")
        return False

    print(f"✓ Validation passed")
    return True
