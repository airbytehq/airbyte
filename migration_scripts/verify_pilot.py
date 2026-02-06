"""
Pre-pilot verification script.

Tests field classification and section grouping on pilot connectors
without making any changes to GSM or 1Password.
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


def verify_connector(connector_name, gsm_credentials, overrides):
    """
    Verify classification and preview for a connector.

    Args:
        connector_name: Full connector name (e.g., "source-stripe")
        gsm_credentials: GSM service account credentials
        overrides: Classification overrides from YAML file

    Returns:
        True if verification passed, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Verifying: {connector_name}")
    print('='*70)

    try:
        # Audit connector with field classification
        classifier = FieldClassifier()
        result = audit_connector(connector_name, gsm_credentials, classifier, overrides)

        # Show field classification for each secret
        print(f"\nField Classification:")
        for secret in result['secrets']:
            print(f"\n  Secret: {secret['secret_name']}")
            print(f"    Filename: {secret['filename']}")
            print(f"    Total fields: {secret['total_fields']}")
            print()
            print(f"    AUTH (→ test-credentials-* sections):")
            for field in secret['auth_fields']:
                print(f"      - {field}")
            print()
            print(f"    CONFIG (→ defaults.yaml in repo):")
            for field in secret['config_fields']:
                print(f"      - {field}")
            print()
            print(f"    LOGIN (→ login section):")
            for field in secret['login_fields']:
                print(f"      - {field}")

            if secret['unknown_fields']:
                print()
                print(f"    ⚠️  UNKNOWN (needs manual review):")
                for unknown in secret['unknown_fields']:
                    print(f"      - {unknown['field']}: {unknown['reason']}")

        # Check migration readiness
        print()
        if not result['migration_ready']:
            print(f"  ❌ Migration BLOCKED: {result['blocked_reason']}")
            print()
            print("  Action required:")
            print("  1. Review unknown fields above")
            print("  2. Add classifications to classification_overrides.yaml")
            print("  3. Re-run verification")
            return False

        print(f"  ✅ Migration ready ({result['total_secrets']} secrets, {result['unique_fingerprints']} unique)")

        # Generate 1Password preview
        print()
        print("="*70)
        print("1Password Structure Preview")
        print("="*70)
        migrator = OnePasswordMigrator(dry_run=True)
        preview = migrator.generate_preview(connector_name, result['secrets'])
        print(preview)

        return True

    except Exception as e:
        print(f"\n❌ Error verifying {connector_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


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


def main():
    """Run verification on all pilot connectors."""
    print("="*70)
    print("Pre-Pilot Verification")
    print("="*70)
    print()
    print("This script verifies field classification and section grouping")
    print("on pilot connectors WITHOUT making any changes.")
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

    # Run verification on each pilot connector
    results = {}
    for connector in PILOT_CONNECTORS:
        results[connector] = verify_connector(connector, gsm_credentials, overrides)

    # Print summary
    print("\n" + "="*70)
    print("Verification Summary")
    print("="*70)
    for connector, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {connector}")

    # Overall result
    print()
    all_passed = all(results.values())
    if all_passed:
        print("="*70)
        print("✅ All verifications passed!")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Review the 1Password structure previews above")
        print("  2. Verify section names and field placement look correct")
        print("  3. Proceed to Phase 1a: Build global CONFIG_ALLOWLIST")
        print("  4. Execute pilot migration")
        sys.exit(0)
    else:
        print("="*70)
        print("❌ Some verifications failed")
        print("="*70)
        print()
        print("Action required:")
        print("  1. Review error messages above")
        print("  2. Fix unknown field classifications")
        print("  3. Re-run verification")
        sys.exit(1)


if __name__ == '__main__':
    # Allow running on specific connector(s)
    if len(sys.argv) > 1:
        # Override pilot connectors with command line args
        PILOT_CONNECTORS = sys.argv[1:]
        print(f"Verifying specific connectors: {', '.join(PILOT_CONNECTORS)}")
        print()

    main()
