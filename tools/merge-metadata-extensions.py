#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Merge interleaved streams metadata extensions into existing metadata.yaml files.
"""

import argparse
import sys
from pathlib import Path

import yaml


def merge_metadata_extension(metadata_path: Path, extension_path: Path) -> None:
    """Merge a metadata extension into an existing metadata.yaml file."""

    with open(metadata_path, "r") as f:
        metadata = yaml.safe_load(f)

    with open(extension_path, "r") as f:
        extension = yaml.safe_load(f)

    if "data" not in metadata:
        metadata["data"] = {}

    metadata["data"].update(extension)

    with open(metadata_path, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="Merge metadata extensions into metadata.yaml files")
    parser.add_argument("metadata_file", help="Path to metadata.yaml file")
    parser.add_argument("extension_file", help="Path to extension YAML file")

    args = parser.parse_args()

    metadata_path = Path(args.metadata_file)
    extension_path = Path(args.extension_file)

    if not metadata_path.exists():
        print(f"Metadata file {metadata_path} not found", file=sys.stderr)
        sys.exit(1)

    if not extension_path.exists():
        print(f"Extension file {extension_path} not found", file=sys.stderr)
        sys.exit(1)

    merge_metadata_extension(metadata_path, extension_path)
    print(f"Merged {extension_path} into {metadata_path}")


if __name__ == "__main__":
    main()
