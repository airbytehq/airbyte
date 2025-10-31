# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys

import tomli


files_to_check = [
    "poe-tasks/poetry-connector-tasks.toml",
    "poe-tasks/manifest-only-connector-tasks.toml",
    "poe-tasks/gradle-connector-tasks.toml",
    "airbyte-integrations/connectors/poe_tasks.toml",
]

for file_path in files_to_check:
    try:
        with open(file_path, "rb") as f:
            tomli.load(f)
        print(f"✓ {file_path} - Valid TOML syntax")
    except Exception as e:
        print(f"✗ {file_path} - TOML syntax error: {e}")
        sys.exit(1)

print("All TOML files have valid syntax!")
