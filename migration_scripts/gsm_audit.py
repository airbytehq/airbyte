"""
GSM Audit Script - Inventory connector secrets without exposing values.

Usage:
    python gsm_audit.py --connector source-stripe
    python gsm_audit.py --all --output gsm_audit_report.json
"""

from ci_credentials.secrets_manager import SecretsManager
from collections import Counter
import hashlib
import json
from pathlib import Path
from field_classifier import FieldClassifier, FieldType


def fingerprint_secret(secret_value: str) -> str:
    """Generate a fingerprint without exposing the value."""
    return hashlib.sha256(secret_value.encode()).hexdigest()[:12]


def analyze_all_connectors(gsm_credentials: dict) -> dict:
    """
    Phase 1a: Analyze ALL connectors to build global CONFIG_ALLOWLIST.

    Identifies fields that:
    - Appear in 10+ connectors
    - Have consistent naming patterns
    - Are likely non-secrets based on cross-connector frequency

    Returns:
        {
            "common_fields": {"start_date": 45, "account_id": 32, ...},
            "suggested_allowlist": ["start_date", "account_id", ...],
            "field_statistics": {...}
        }
    """
    from collections import Counter

    # Get list of all Coral connectors
    connectors = get_all_coral_connectors()

    field_frequency = Counter()
    field_examples = {}

    for connector in connectors:
        try:
            manager = SecretsManager(connector, gsm_credentials)
            secrets = manager.read_from_gsm()

            for secret in secrets:
                config = json.loads(secret.value)
                for field_name in config.keys():
                    field_lower = field_name.lower()
                    field_frequency[field_lower] += 1

                    if field_lower not in field_examples:
                        field_examples[field_lower] = []
                    field_examples[field_lower].append(connector)
        except Exception as e:
            print(f"Skipping {connector}: {e}")
            continue

    # Fields in 10+ connectors are very likely config
    threshold = 10
    suggested_allowlist = [
        field for field, count in field_frequency.items()
        if count >= threshold
    ]

    return {
        "common_fields": dict(field_frequency.most_common(50)),
        "suggested_allowlist": suggested_allowlist,
        "threshold_used": threshold,
        "total_connectors_analyzed": len(connectors),
    }


def flatten_nested_config(config: dict, parent_key: str = '', separator: str = '_') -> dict:
    """
    Flatten nested credential dictionaries using innermost field names.

    Example:
        {"auth_method": {"auth_method": "oauth", "client_secret": "..."}}
        becomes
        {"auth_method": "oauth", "client_secret": "..."}

    Falls back to full path if there are name collisions.

    Args:
        config: Configuration dict (may contain nested dicts)
        parent_key: Parent key for recursion
        separator: Separator for flattened keys when needed (default: underscore)

    Returns:
        Flattened dict with innermost keys (or full path on collision)
    """
    # First pass: collect all flattened paths and their innermost keys
    paths = {}  # innermost_key -> list of (full_path, value)

    def collect_paths(cfg: dict, parent: str = ''):
        for key, value in cfg.items():
            full_path = f"{parent}{separator}{key}" if parent else key

            if isinstance(value, dict):
                collect_paths(value, full_path)
            else:
                # Store the innermost key and its full path
                innermost = key
                if innermost not in paths:
                    paths[innermost] = []
                paths[innermost].append((full_path, value))

    collect_paths(config, parent_key)

    # Second pass: build result, using innermost key or full path on collision
    flattened = {}
    for innermost_key, path_list in paths.items():
        if len(path_list) == 1:
            # No collision - use innermost key
            flattened[innermost_key] = path_list[0][1]
        else:
            # Collision detected - use full paths
            for full_path, value in path_list:
                flattened[full_path] = value

    return flattened


def audit_connector(connector_name: str, gsm_credentials: dict,
                    classifier: FieldClassifier,
                    overrides: dict = None) -> dict:
    """
    Audit a single connector's GSM secrets with field classification.

    Args:
        connector_name: Connector to audit
        gsm_credentials: GSM access credentials
        classifier: FieldClassifier instance with CONFIG_ALLOWLIST populated
        overrides: Manual classification overrides from YAML file

    Returns:
        Dict with classified fields, unknowns flagged, and migration readiness
    """
    if overrides is None:
        overrides = {}

    manager = SecretsManager(connector_name, gsm_credentials)
    secrets = manager.read_from_gsm()

    results = []
    all_unknowns = []

    for secret in secrets:
        config = json.loads(secret.value)

        # Flatten nested credential structures
        flattened_config = flatten_nested_config(config)

        auth_fields = []
        config_fields = []
        login_fields = []
        unknown_fields = []

        for field_name, field_value in flattened_config.items():
            # Check manual overrides first
            override_key = f"{connector_name}.{field_name}"
            if override_key in overrides:
                classification = overrides[override_key]
                if classification == "secret":
                    auth_fields.append(field_name)
                else:
                    config_fields.append(field_name)
                continue

            # Use classifier
            result = classifier.classify(field_name, field_value)

            if result.field_type == FieldType.UNKNOWN:
                unknown_fields.append({
                    "field": field_name,
                    "reason": result.reason,
                })
                all_unknowns.append(field_name)
            elif result.field_type == FieldType.SECRET:
                auth_fields.append(field_name)
            elif result.field_type == FieldType.LOGIN:
                login_fields.append(field_name)
            else:
                config_fields.append(field_name)

        # Post-processing: If we have login fields (username/email), move password to login
        if login_fields and "password" in auth_fields:
            auth_fields.remove("password")
            login_fields.append("password")

        results.append({
            "secret_name": secret.name,
            "filename": secret.configuration_file_name,
            "auth_fields": auth_fields,  # List of field names only
            "config_fields": config_fields,  # List of field names only
            "login_fields": login_fields,  # List of login credential field names
            "unknown_fields": unknown_fields,  # Field names + reasons, no values
            "raw_config": flattened_config,  # SECURITY: Contains actual secret values - never log this!
            "fingerprint": fingerprint_secret(secret.value),
            "total_fields": len(flattened_config),
        })

    fingerprints = [r["fingerprint"] for r in results]
    unique_fingerprints = set(fingerprints)

    # Migration readiness check
    migration_ready = len(all_unknowns) == 0

    return {
        "connector": connector_name,
        "secrets": results,
        "total_secrets": len(results),
        "unique_fingerprints": len(unique_fingerprints),
        "has_duplicates": len(fingerprints) != len(unique_fingerprints),
        "unknown_fields": list(set(all_unknowns)),
        "migration_ready": migration_ready,
        "blocked_reason": None if migration_ready else "Unknown fields require manual classification",
    }


def analyze_gsm_secrets(connector_name: str, gsm_credentials: dict) -> None:
    """Analyze and report on GSM secrets for a connector."""
    manager = SecretsManager(connector_name, gsm_credentials)
    secrets = manager.read_from_gsm()

    fingerprints = {}
    for secret in secrets:
        config = json.loads(secret.value)
        fp = fingerprint_secret(secret.value)

        fingerprints.setdefault(fp, []).append({
            "name": secret.name,
            "filename": secret.configuration_file_name,
            "fields": list(config.keys()),
        })

    print(f"\n=== Audit Report for {connector_name} ===\n")
    print(f"Total secrets: {len(secrets)}")
    print(f"Unique credentials: {len(fingerprints)}")

    for fp, entries in fingerprints.items():
        if len(entries) > 1:
            print(f"\nDuplicate group (fingerprint: {fp}):")
            for e in entries:
                print(f"  - {e['name']} ({e['filename']})")


def categorize_connectors(audit_results: list[dict]) -> dict:
    """Categorize connectors by migration complexity."""
    simple = []
    moderate = []
    complex_list = []

    for result in audit_results:
        connector = result["connector"]
        total = result["total_secrets"]

        if total == 1:
            simple.append(connector)
        elif total <= 3:
            moderate.append(connector)
        else:
            complex_list.append(connector)

    return {"simple": simple, "moderate": moderate, "complex": complex_list}


def run_audit_with_review(connector_name: str, gsm_credentials: dict):
    """Run audit and handle unknown fields."""

    # Load Phase 1a results
    allowlist_data = load_json("phase1a_allowlist.json")
    classifier = FieldClassifier()
    classifier.CONFIG_ALLOWLIST = set(allowlist_data["suggested_allowlist"])

    # Load manual overrides
    overrides = load_yaml("classification_overrides.yaml")

    # Run audit
    result = audit_connector(connector_name, gsm_credentials, classifier, overrides)

    if not result["migration_ready"]:
        print(f"\n⚠️  {connector_name} blocked: {len(result['unknown_fields'])} unknown fields")
        print("\nUnknown fields requiring manual classification:")
        for field in result["unknown_fields"]:
            print(f"  - {field}")
        print(f"\nAdd to classification_overrides.yaml:")
        for field in result["unknown_fields"]:
            print(f"{connector_name}.{field}: [secret|config]")
        return None

    print(f"✓ {connector_name} ready for migration")
    return result
