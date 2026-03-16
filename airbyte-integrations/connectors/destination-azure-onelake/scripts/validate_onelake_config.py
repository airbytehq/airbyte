#!/usr/bin/env python3
"""
Validate Microsoft OneLake destination config.json without using Airbyte.

Usage:
  # Validate structure and value formats only (no network):
  python scripts/validate_onelake_config.py [path/to/config.json]

  # With virtualenv (recommended for --connectivity):
  python3 -m venv .venv
  .venv/bin/pip install -r scripts/requirements-validate.txt
  .venv/bin/python scripts/validate_onelake_config.py [path/to/config.json] --connectivity

  # Or install deps globally and run with --connectivity:
  pip install -r scripts/requirements-validate.txt
  python scripts/validate_onelake_config.py [path/to/config.json] --connectivity

Defaults to sample_secrets/config.json if no path given.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# UUID v4-ish pattern (hex in 8-4-4-4-12)
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

REQUIRED_KEYS = [
    "azure_blob_storage_account_name",
    "azure_blob_storage_container_name",
    "azure_tenant_id",
    "azure_client_id",
    "azure_client_secret",
    "format",
]

VALID_FORMAT_TYPES = {"JSONL", "PARQUET", "CSV"}


def load_config(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_uuid(name: str, value: str) -> list[str]:
    errs = []
    if not value or not value.strip():
        errs.append(f"{name}: must be non-empty")
    elif not UUID_RE.match(value.strip()):
        errs.append(f"{name}: must be a valid UUID (got: {value!r})")
    return errs


def validate_format(obj: object) -> list[str]:
    errs = []
    if not isinstance(obj, dict):
        errs.append("format: must be an object")
        return errs
    ft = obj.get("format_type")
    if not ft:
        errs.append("format: missing 'format_type'")
    elif ft.upper() not in VALID_FORMAT_TYPES:
        errs.append(
            f"format: format_type must be one of {sorted(VALID_FORMAT_TYPES)} (got: {ft!r})"
        )
    return errs


def validate_config(config: dict) -> list[str]:
    errors = []

    for key in REQUIRED_KEYS:
        if key not in config:
            errors.append(f"Missing required key: {key}")
            continue
        val = config[key]

        if key == "azure_blob_storage_account_name":
            if not isinstance(val, str) or not val.strip():
                errors.append("azure_blob_storage_account_name: must be non-empty string (workspace name or GUID)")
        elif key == "azure_blob_storage_container_name":
            if not isinstance(val, str) or not val.strip():
                errors.append(
                    "azure_blob_storage_container_name: must be non-empty string (e.g. 'lakehouse_raw' or 'lakehouse_raw.Lakehouse')"
                )
            elif "." in val:
                part = val.strip().split(".")[-1]
                if part.lower() not in ("lakehouse", "warehouse", "kql", "eventstream", "ml"):
                    errors.append(
                        f"azure_blob_storage_container_name: if using ItemName.ItemType, ItemType should be e.g. Lakehouse (got: {part!r})"
                    )
        elif key == "azure_tenant_id":
            if not isinstance(val, str):
                errors.append("azure_tenant_id: must be string")
            else:
                errors.extend(validate_uuid("azure_tenant_id", val))
        elif key == "azure_client_id":
            if not isinstance(val, str):
                errors.append("azure_client_id: must be string")
            else:
                errors.extend(validate_uuid("azure_client_id", val))
        elif key == "azure_client_secret":
            if not isinstance(val, str) or not val.strip():
                errors.append("azure_client_secret: must be non-empty string")
        elif key == "format":
            errors.extend(validate_format(val))

    return errors


def test_connectivity(config: dict) -> list[str]:
    """Optional: upload a tiny blob to OneLake and delete it. Returns list of error messages."""
    import warnings
    # Suppress urllib3 NotOpenSSLWarning on macOS (LibreSSL vs OpenSSL) before loading azure
    warnings.filterwarnings("ignore", module="urllib3")
    try:
        from azure.identity import ClientSecretCredential
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        return [
            "Connectivity test requires: pip install azure-storage-blob azure-identity"
        ]
    workspace = (config.get("azure_blob_storage_account_name") or "").strip()
    lakehouse_raw = (config.get("azure_blob_storage_container_name") or "").strip()
    tenant_id = (config.get("azure_tenant_id") or "").strip()
    client_id = (config.get("azure_client_id") or "").strip()
    client_secret = (config.get("azure_client_secret") or "").strip()

    if not all([workspace, lakehouse_raw, tenant_id, client_id, client_secret]):
        return ["Connectivity test: all auth and target fields must be set"]

    # OneLake: container = workspace, path = item.itemtype/Files/...
    container_name = workspace
    item_path = f"{lakehouse_raw}.Lakehouse" if "." not in lakehouse_raw else lakehouse_raw
    blob_name = f"{item_path}/Files/airbyte/_onelake_config_test"

    endpoint = "https://onelake.blob.fabric.microsoft.com"
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    client = BlobServiceClient(account_url=endpoint, credential=credential)
    container = client.get_container_client(container_name)
    blob = container.get_blob_client(blob_name)

    try:
        blob.upload_blob(b"airbyte-onelake-config-test", overwrite=True)
    except Exception as e:
        return [f"Connectivity test failed (upload): {e}"]

    try:
        blob.delete_blob()
    except Exception as e:
        # OneLake returns HTTP 200 for delete while the Blob SDK expects 202;
        # the SDK raises "Operation returned an invalid status 'OK'" - treat as success.
        if "invalid status" in str(e) and "OK" in str(e):
            pass  # OneLake quirk: success
        else:
            return [f"Connectivity test failed (delete): {e}"]

    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OneLake destination config.json (no Airbyte)."
    )
    parser.add_argument(
        "config_path",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "sample_secrets" / "config.json",
        help="Path to config.json (default: sample_secrets/config.json)",
    )
    parser.add_argument(
        "--connectivity",
        action="store_true",
        help="Also run a quick OneLake upload/delete test (requires azure-storage-blob, azure-identity)",
    )
    args = parser.parse_args()

    if not args.config_path.exists():
        print(f"Error: config file not found: {args.config_path}", file=sys.stderr)
        return 1

    try:
        config = load_config(args.config_path)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.config_path}: {e}", file=sys.stderr)
        return 1

    errors = validate_config(config)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("Config validation passed.")
    print("  Workspace (account):", config.get("azure_blob_storage_account_name"))
    print("  Lakehouse (item):   ", config.get("azure_blob_storage_container_name"))
    print("  Format:             ", config.get("format", {}).get("format_type"))

    if args.connectivity:
        print("\nRunning connectivity test (upload + delete test blob)...")
        conn_errors = test_connectivity(config)
        if conn_errors:
            print("Connectivity test failed:", file=sys.stderr)
            for e in conn_errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        print("Connectivity test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
