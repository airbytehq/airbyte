"""Simple script to download secrets from GCS.

Usage:
    pipx install uv
    uv run get_secrets.py
"""
# Inline dependency metadata for `uv`:
# /// script
# requires-python = "==3.10"
# dependencies = [
#     "airbyte",
#     "google-cloud-secret-manager",
# ]
# ///

from __future__ import annotations

from pathlib import Path

from google.cloud import secretmanager_v1 as secretmanager

import airbyte as ab
from airbyte.secrets import GoogleGSMSecretManager, SecretHandle


AIRBYTE_INTERNAL_GCP_PROJECT = "dataline-integration-testing"


def main() -> None:
    secret_mgr = GoogleGSMSecretManager(
        project=AIRBYTE_INTERNAL_GCP_PROJECT,
        credentials_json=ab.get_secret("GCP_GSM_CREDENTIALS"),
    )

    secret: SecretHandle
    for secret in secret_mgr.fetch_connector_secrets("source-s3"):
        response = secret_mgr.secret_client.get_secret(
            secretmanager.GetSecretRequest(name=secret.secret_name),
        )
        labels: dict[str, str] = response.labels
        if "filename" in labels:
            secret_file_path = Path(f'secrets/{labels["filename"]}.json')
            print(f"Writing '{secret.secret_name.split('/')[-1]}' secret to '{secret_file_path}'")
            secret_file_path.write_text(secret.get_value())


if __name__ == "__main__":
    main()
