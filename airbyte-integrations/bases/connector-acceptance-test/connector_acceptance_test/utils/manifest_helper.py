# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_protocol.models import ConnectorSpecification

MANIFEST_FILE_NAMES = [
    "manifest.yaml",
    "manifest.yml",
]


def is_manifest_file(file_name: Path) -> bool:
    return file_name.name in MANIFEST_FILE_NAMES


def parse_manifest_spec(manifest_obj: dict) -> dict:
    valid_spec_obj = {
        "connectionSpecification": manifest_obj["spec"]["connection_specification"],
    }
    return ConnectorSpecification.parse_obj(valid_spec_obj)
