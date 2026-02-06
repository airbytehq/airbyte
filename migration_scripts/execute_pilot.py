"""
Execute pilot migration for verified connectors.

This script performs the ACTUAL migration:
1. Migrates auth fields to 1Password
2. Creates defaults.yaml files with config values
3. Verifies migration success

Usage:
    python execute_pilot.py
    python execute_pilot.py source-stripe  # Single connector
"""

from gsm_audit import audit_connector
from gsm_to_1password import OnePasswordMigrator
from field_classifier import FieldClassifier
import json
import sys
import os
import yaml
from pathlib import Path


# Pilot connectors for testing
PILOT_CONNECTORS = [
    'source-stripe',      # Simple API key auth
    'source-github',      # Token-based auth
    'source-service-now'  # Username + password login
]


def load_classification_overrides():
    """Load manual classification overrides from YAML file."""
    overrides_file = Path(__file__).parent / "classification_overrides.yaml"
    if not overrides_file.exists():
        return {}

    with open(overrides_file) as f:
        data = yaml.safe_load(f) or {}

    # Flatten global overrides into connector-specific format
    overrides = {}
    for key, value in data.items():
        if key == "_global":
            # Global overrides apply to all connectors
            global_overrides = data.get("_global") or {}
            for field, classification in global_overrides.items():
                overrides[f"_global.{field}"] = classification
        elif key not in ["_global"]:
            # Connector-specific overrides
            overrides[key] = value

    return overrides


def load_gsm_credentials():
    """
    Load GSM credentials from environment or file.

    Returns:
        GSM credentials dict
    """
    # Try environment variables first (support both naming conventions)
    gsm_creds_json = os.getenv('GCP_GSM_CREDENTIALS') or os.getenv('GSM_CREDENTIALS')
    if gsm_creds_json:
        return json.loads(gsm_creds_json)

    # Try loading from file
    creds_file = os.path.expanduser('~/.gsm_credentials.json')
    if os.path.exists(creds_file):
        with open(creds_file) as f:
            return json.load(f)

    raise RuntimeError(
        "GSM credentials not found. Set GCP_GSM_CREDENTIALS or GSM_CREDENTIALS env var or create ~/.gsm_credentials.json"
    )


def normalize_config_field_name(field_name: str) -> str:
    """
    Normalize config field names for defaults.yaml.

    Removes flattening prefixes for cleaner config files.

    Examples:
        credentials_api_url → api_url
        credentials_personal_access_token → personal_access_token
    """
    # Remove common prefixes from flattened nested structures
    if field_name.startswith("credentials_"):
        return field_name[len("credentials_"):]
    return field_name


def create_defaults_yaml(connector_name: str, variants: dict[str, dict], airbyte_repo_root: Path):
    """
    Create defaults.yaml file with config values for each variant.

    Args:
        connector_name: Full connector name (e.g., "source-stripe")
        variants: Dict of variants with auth/config data from _group_by_variant()
        airbyte_repo_root: Path to airbyte repo root

    Returns:
        Path to created defaults.yaml file
    """
    # Create path: airbyte-integrations/connectors/{connector_name}/integration_tests/defaults.yaml
    connector_dir = airbyte_repo_root / "airbyte-integrations" / "connectors" / connector_name / "integration_tests"
    connector_dir.mkdir(parents=True, exist_ok=True)

    # Build YAML structure with config values for each variant
    # Normalize field names to remove flattening prefixes
    defaults_data = {}
    for variant_name, variant_data in variants.items():
        if variant_data["config"]:
            normalized_config = {
                normalize_config_field_name(field): value
                for field, value in variant_data["config"].items()
            }
            defaults_data[variant_name] = normalized_config

    # Write defaults.yaml
    defaults_file = connector_dir / "defaults.yaml"
    with open(defaults_file, 'w') as f:
        yaml.dump(defaults_data, f, default_flow_style=False, sort_keys=False)

    print(f"  ✅ Created {defaults_file}")
    return defaults_file


def execute_migration(connector_name, gsm_credentials, overrides, airbyte_repo_root: Path):
    """
    Execute migration for a connector.

    Args:
        connector_name: Full connector name (e.g., "source-stripe")
        gsm_credentials: GSM service account credentials
        overrides: Classification overrides from YAML file
        airbyte_repo_root: Path to airbyte repo root

    Returns:
        True if migration succeeded, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Migrating: {connector_name}")
    print('='*70)

    try:
        # Step 1: Audit connector with field classification
        classifier = FieldClassifier()
        result = audit_connector(connector_name, gsm_credentials, classifier, overrides)

        # Check migration readiness
        if not result['migration_ready']:
            print(f"  ❌ Migration BLOCKED: {result['blocked_reason']}")
            print()
            print("  Action required:")
            print("  1. Review unknown fields above")
            print("  2. Add classifications to classification_overrides.yaml")
            print("  3. Re-run migration")
            return False

        print(f"  ✅ Classification complete ({result['total_secrets']} secrets, {result['unique_fingerprints']} unique)")

        # Step 2: Migrate auth fields to 1Password (ACTUAL EXECUTION)
        print()
        print("  Migrating auth fields to 1Password...")
        migrator = OnePasswordMigrator(dry_run=False)  # REAL MIGRATION
        migration_result = migrator.migrate_connector(connector_name, result['secrets'])

        if migration_result.status == "failed":
            print(f"  ❌ Migration failed: {migration_result.error}")
            return False

        print(f"  ✅ 1Password migration {migration_result.status}")
        print(f"     - Sections: {', '.join(migration_result.sections_created)}")
        print(f"     - Fields migrated: {migration_result.fields_migrated}")

        # Step 3: Create defaults.yaml with config values
        print()
        print("  Creating defaults.yaml with config values...")
        variants, login_sections = migrator._group_by_variant(result['secrets'])
        defaults_file = create_defaults_yaml(connector_name, variants, airbyte_repo_root)

        # Step 4: Show summary
        print()
        print(f"  ✅ Migration complete!")
        print(f"     - Auth fields → 1Password vault: replication-connector-credentials")
        print(f"     - Config values → {defaults_file}")

        return True

    except Exception as e:
        print(f"\n❌ Error migrating {connector_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Execute pilot migration on all pilot connectors."""
    print("="*70)
    print("Pilot Migration Execution")
    print("="*70)
    print()
    print("This script performs ACTUAL migration:")
    print("  1. Migrates auth fields to 1Password")
    print("  2. Creates defaults.yaml files with config values")
    print()

    # Load GSM credentials
    try:
        gsm_credentials = load_gsm_credentials()
        print("✅ GSM credentials loaded")
    except Exception as e:
        print(f"❌ Failed to load GSM credentials: {e}")
        print()
        print("Setup instructions:")
        print("  Option 1: Set environment variable")
        print("    export GCP_GSM_CREDENTIALS='{...}'")
        print("    or")
        print("    export GSM_CREDENTIALS='{...}'")
        print()
        print("  Option 2: Create credentials file")
        print("    echo '{...}' > ~/.gsm_credentials.json")
        sys.exit(1)

    # Load classification overrides
    try:
        overrides = load_classification_overrides()
        override_count = len([k for k in overrides.keys() if not k.startswith("_global")])
        if override_count > 0:
            print(f"✅ Loaded {override_count} classification overrides")
    except Exception as e:
        print(f"⚠️  Warning: Failed to load classification overrides: {e}")
        overrides = {}

    # Determine airbyte repo root (migration_scripts is in the repo)
    airbyte_repo_root = Path(__file__).parent.parent
    print(f"✅ Airbyte repo root: {airbyte_repo_root}")

    # Verify airbyte-integrations directory exists
    airbyte_integrations = airbyte_repo_root / "airbyte-integrations"
    if not airbyte_integrations.exists():
        print(f"❌ Error: {airbyte_integrations} does not exist")
        print("   Make sure you're running this from the airbyte repo")
        sys.exit(1)

    # Execute migration on each pilot connector
    print()
    results = {}
    for connector in PILOT_CONNECTORS:
        results[connector] = execute_migration(connector, gsm_credentials, overrides, airbyte_repo_root)

    # Print summary
    print("\n" + "="*70)
    print("Migration Summary")
    print("="*70)
    for connector, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} {connector}")

    # Overall result
    print()
    all_success = all(results.values())
    if all_success:
        print("="*70)
        print("✅ All migrations completed successfully!")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Verify 1Password items:")
        print("     op item list --vault replication-connector-credentials")
        print("  2. Review defaults.yaml files:")
        print("     find airbyte-integrations/connectors/source-*/integration_tests/defaults.yaml")
        print("  3. Test connector access with new structure")
        print("  4. Commit changes and proceed with full migration rollout")
        sys.exit(0)
    else:
        print("="*70)
        print("❌ Some migrations failed")
        print("="*70)
        print()
        print("Action required:")
        print("  1. Review error messages above")
        print("  2. Fix issues (classifications, 1Password access, etc.)")
        print("  3. Re-run migration")
        sys.exit(1)


if __name__ == '__main__':
    # Allow running on specific connector(s)
    if len(sys.argv) > 1:
        # Override pilot connectors with command line args
        PILOT_CONNECTORS = sys.argv[1:]
        print(f"Migrating specific connectors: {', '.join(PILOT_CONNECTORS)}")
        print()

    main()
