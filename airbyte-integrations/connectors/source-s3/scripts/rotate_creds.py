# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Script to rotate AWS credentials for integration tests.

Uses PyAirbyte to rotate AWS credentials for integration tests.

Usage:
    cd scripts
    poetry run python rotate_creds.py

Not working:
    pipx install uv
    uv run --no-project scripts/rotate_creds.py

Inline dependency metadata for `uv`:

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "airbyte",  # PyAirbyte
# ]
# ///
"""

from __future__ import annotations

import json
from typing import Any, cast

from airbyte.secrets import get_secret
from airbyte.secrets.google_gsm import GoogleGSMSecretManager, GSMSecretHandle

AIRBYTE_INTERNAL_GCP_PROJECT = "dataline-integration-testing"
CONNECTOR_NAME = "source-s3"

SECRET_MGR = GoogleGSMSecretManager(
    project=AIRBYTE_INTERNAL_GCP_PROJECT,
    credentials_json=get_secret("GCP_GSM_CREDENTIALS"),
)

OLD_KEYS = [  # Expects one or more old AWS key IDs (CSV format)
    key_id.strip() for key_id in cast(str, get_secret("OLD_AWS_KEY_IDS")).split(",")
]
NEW_KEY = get_secret("NEW_AWS_KEY_ID")  # Expects the new AWS Key ID
NEW_SECRET_KEY = get_secret("NEW_AWS_SECRET_KEY")  # Expects the new AWS Secret Key

LIMIT = 1  # Limit the number of secrets to rotate. Use this if you aren't 100% confident.


def _replace_credentials(
    secret_dict: dict,
    old_keys: list[str],
    new_key: str,
    new_secret_key: str,
) -> bool:
    is_changed = False

    if "aws_access_key_id" in secret_dict and secret_dict["aws_access_key_id"] in old_keys:
        secret_dict["aws_access_key_id"] = new_key
        secret_dict["aws_secret_access_key"] = new_secret_key
        is_changed = True

    for value in secret_dict.values():
        # Traverse nested dictionaries recursively
        if isinstance(value, dict):
            is_changed = (
                _replace_credentials(
                    secret_dict=value,
                    old_keys=old_keys,
                    new_key=new_key,
                    new_secret_key=new_secret_key,
                )
                or is_changed
            )

    return is_changed


def _set_secret_json(secret_dict: dict, secret_handle: GSMSecretHandle) -> None:
    secret_client = secret_handle.parent.secret_client
    new_secret_str = json.dumps(secret_dict, indent=2)
    payload_bytes = new_secret_str.encode("UTF-8")
    secret_client.add_secret_version(
        request={
            "parent": secret_handle.secret_name,
            "payload": {
                "data": payload_bytes,
            },
        }
    )

    # Optionally, disable the old version to prevent accidental use.
    # For now, we'll leave it enabled and let the user disable it manually.
    # client.disable_secret_version(
    #     request={"name": f"{secret_name}/versions/{secret.version_id}"}
    # )


def main() -> None:
    modified_count = 0
    secret: GSMSecretHandle
    for secret in SECRET_MGR.fetch_connector_secrets(CONNECTOR_NAME):
        secret_dict: dict[str, Any] = secret.parse_json()
        is_changed = _replace_credentials(
            secret_dict=secret_dict,
            old_keys=OLD_KEYS,
            new_key=NEW_KEY,
            new_secret_key=NEW_SECRET_KEY,
        )
        if is_changed:
            _set_secret_json(secret_dict=secret_dict, secret_handle=secret)
            print(f"Rotated credentials for secret: {secret.secret_name}")
            modified_count += 1

        if modified_count >= LIMIT:
            print(f"Rotated max of {LIMIT} secrets. Exiting.")
            return

    print(f"Rotation complete. Rotated {LIMIT} secrets successfully.")


if __name__ == "__main__":
    main()
