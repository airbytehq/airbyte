#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Apply all generated metadata extensions to their corresponding metadata.yaml files.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).parent.parent
    connectors_dir = repo_root / "airbyte-integrations" / "connectors"

    extension_files = list(repo_root.glob("*_metadata_extension.yaml"))

    if not extension_files:
        print("No metadata extension files found")
        sys.exit(1)

    print(f"Found {len(extension_files)} metadata extensions to apply")

    success_count = 0
    error_count = 0

    for extension_file in extension_files:
        connector_name = extension_file.name.replace("_metadata_extension.yaml", "")
        metadata_file = connectors_dir / connector_name / "metadata.yaml"

        if not metadata_file.exists():
            print(f"Warning: metadata.yaml not found for {connector_name}")
            error_count += 1
            continue

        result = subprocess.run(
            [sys.executable, "tools/merge-metadata-extensions.py", str(metadata_file), str(extension_file)], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Error merging {connector_name}: {result.stderr}")
            error_count += 1
        else:
            print(f"✓ Applied extension for {connector_name}")
            extension_file.unlink()
            success_count += 1

    print(f"\nSummary: {success_count} successful, {error_count} errors")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
