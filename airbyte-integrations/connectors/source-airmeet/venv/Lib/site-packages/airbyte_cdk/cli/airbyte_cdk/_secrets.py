# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""**Secret management commands.**

This module provides commands for managing secrets for Airbyte connectors.

**Usage:**

```bash
# Fetch secrets
airbyte-cdk secrets fetch --connector-name source-github
airbyte-cdk secrets fetch --connector-directory /path/to/connector
airbyte-cdk secrets fetch  # Run from within a connector directory

# List secrets (without fetching)
airbyte-cdk secrets list --connector-name source-github
airbyte-cdk secrets list --connector-directory /path/to/connector
```

**Usage without pre-installing (stateless):**

```bash
pipx run airbyte-cdk secrets fetch ...
uvx airbyte-cdk secrets fetch ...
```

The command retrieves secrets from Google Secret Manager based on connector
labels and writes them to the connector's `secrets` directory.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import requests
import rich_click as click
import yaml
from click import style
from rich.console import Console
from rich.table import Table

from airbyte_cdk.cli.airbyte_cdk.exceptions import ConnectorSecretWithNoValidVersionsError
from airbyte_cdk.utils.connector_paths import (
    resolve_connector_name,
    resolve_connector_name_and_directory,
)

GCP_PROJECT_ID: str = os.environ.get("GCP_PROJECT_ID", "") or "dataline-integration-testing"
# We put the `or` outside the `get()` because we want the `GCP_PROJECT_ID`
# env var to be ignored if it contains an empty string, such as in CI where the
# workflow might set it to a value that is itself actually missing or unset.
"""The GCP project ID to use for fetching integration test secrets."""

CONNECTOR_LABEL = "connector"
GLOBAL_MASK_KEYS_URL = "https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml"

logger = logging.getLogger("airbyte-cdk.cli.secrets")

try:
    from google.cloud import secretmanager_v1 as secretmanager
    from google.cloud.secretmanager_v1 import Secret
except ImportError:
    # If the package is not installed, we will raise an error in the CLI command.
    secretmanager = None  # type: ignore
    Secret = None  # type: ignore


@click.group(
    name="secrets",
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown) # type: ignore
)
def secrets_cli_group() -> None:
    """Secret management commands."""
    pass


@secrets_cli_group.command()
@click.argument(
    "connector",
    required=False,
    type=str,
    metavar="[CONNECTOR]",
)
@click.option(
    "--gcp-project-id",
    type=str,
    default=GCP_PROJECT_ID,
    help=(
        "GCP project ID for retrieving integration tests credentials. "
        "Defaults to the value of the `GCP_PROJECT_ID` environment variable, if set."
    ),
)
@click.option(
    "--print-ci-secrets-masks",
    help="Print GitHub CI mask for secrets.",
    type=bool,
    is_flag=True,
    default=None,
)
def fetch(
    connector: str | Path | None = None,
    gcp_project_id: str = GCP_PROJECT_ID,
    print_ci_secrets_masks: bool | None = None,
) -> None:
    """Fetch secrets for a connector from Google Secret Manager.

    This command fetches secrets for a connector from Google Secret Manager and writes them
    to the connector's secrets directory.

    [CONNECTOR] can be a connector name (e.g. 'source-pokeapi'), a path to a connector directory, or omitted to use the current working directory.
    If a string containing '/' is provided, it is treated as a path. Otherwise, it is treated as a connector name.

    If no connector name or directory is provided, we will look within the current working
    directory. If the current working directory is not a connector directory (e.g. starting
    with 'source-') and no connector name or path is provided, the process will fail.

    The `--print-ci-secrets-masks` option will print the GitHub CI mask for the secrets.
    This is useful for masking secrets in CI logs.

    WARNING: The `--print-ci-secrets-masks` option causes the secrets to be printed in clear text to
    `STDOUT`. For security reasons, this argument will be ignored if the `CI` environment
    variable is not set.
    """
    click.echo("Fetching secrets...", err=True)

    client = _get_gsm_secrets_client()
    connector_name, connector_directory = resolve_connector_name_and_directory(connector)
    secrets_dir = _get_secrets_dir(
        connector_directory=connector_directory,
        connector_name=connector_name,
        ensure_exists=True,
    )
    secrets = _fetch_secret_handles(
        connector_name=connector_name,
        gcp_project_id=gcp_project_id,
    )
    # Fetch and write secrets
    secret_count = 0
    exceptions = []

    for secret in secrets:
        secret_file_path = _get_secret_filepath(
            secrets_dir=secrets_dir,
            secret=secret,
        )
        try:
            _write_secret_file(
                secret=secret,
                client=client,
                file_path=secret_file_path,
                connector_name=connector_name,
                gcp_project_id=gcp_project_id,
            )
            click.echo(f"Secret written to: {secret_file_path.absolute()!s}", err=True)
            secret_count += 1
        except ConnectorSecretWithNoValidVersionsError as e:
            exceptions.append(e)
            click.echo(
                f"Failed to retrieve secret '{e.secret_name}': No enabled version found", err=True
            )

    if secret_count == 0 and not exceptions:
        click.echo(
            f"No secrets found for connector: '{connector_name}'",
            err=True,
        )

    if exceptions:
        error_message = f"Failed to retrieve {len(exceptions)} secret(s)"
        click.echo(
            style(
                error_message,
                fg="red",
            ),
            err=True,
        )
        if secret_count == 0:
            raise exceptions[0]

    if print_ci_secrets_masks and "CI" not in os.environ:
        click.echo(
            "The `--print-ci-secrets-masks` option is only available in CI environments. "
            "The `CI` env var is either not set or not set to a truthy value. "
            "Skipping printing secret masks.",
            err=True,
        )
        print_ci_secrets_masks = False
    elif print_ci_secrets_masks is None:
        # If not explicitly set, we check if we are in a CI environment
        # and set to True if so.
        print_ci_secrets_masks = os.environ.get("CI", "") != ""

    if print_ci_secrets_masks:
        _print_ci_secrets_masks(
            secrets_dir=secrets_dir,
        )


@secrets_cli_group.command("list")
@click.argument(
    "connector",
    required=False,
    type=str,
    metavar="[CONNECTOR]",
)
@click.option(
    "--gcp-project-id",
    type=str,
    default=GCP_PROJECT_ID,
    help=(
        "GCP project ID for retrieving integration tests credentials. "
        "Defaults to the value of the `GCP_PROJECT_ID` environment variable, if set."
    ),
)
def list_(
    connector: str | Path | None = None,
    *,
    gcp_project_id: str = GCP_PROJECT_ID,
) -> None:
    """List secrets for a connector from Google Secret Manager.

    This command fetches secrets for a connector from Google Secret Manager and prints
    them as a table.

    [CONNECTOR] can be a connector name (e.g. 'source-pokeapi'), a path to a connector directory, or omitted to use the current working directory.
    If a string containing '/' is provided, it is treated as a path. Otherwise, it is treated as a connector name.

    If no connector name or directory is provided, we will look within the current working
    directory. If the current working directory is not a connector directory (e.g. starting
    with 'source-') and no connector name or path is provided, the process will fail.
    """
    click.echo("Scanning secrets...", err=True)

    connector_name, _ = resolve_connector_name_and_directory(connector)
    secrets: list[Secret] = _fetch_secret_handles(  # type: ignore
        connector_name=connector_name,
        gcp_project_id=gcp_project_id,
    )

    if not secrets:
        click.echo(
            f"No secrets found for connector: '{connector_name}'",
            err=True,
        )
        return
    # print a rich table with the secrets
    click.echo(
        style(
            f"Secrets for connector '{connector_name}' in project '{gcp_project_id}':",
            fg="green",
        )
    )

    console = Console()
    table = Table(title=f"'{connector_name}' Secrets")
    table.add_column("Name", justify="left", style="cyan", overflow="fold")
    table.add_column("Labels", justify="left", style="magenta", overflow="fold")
    table.add_column("Created", justify="left", style="blue", overflow="fold")
    for secret in secrets:
        full_secret_name = secret.name
        secret_name = _extract_secret_name(full_secret_name)
        secret_url = _get_secret_url(secret_name, gcp_project_id)
        table.add_row(
            f"[link={secret_url}]{secret_name}[/link]",
            "\n".join([f"{k}={v}" for k, v in secret.labels.items()]),
            str(secret.create_time),
        )

    console.print(table)


def _extract_secret_name(secret_name: str) -> str:
    """Extract the secret name from a fully qualified secret path.

    Handles different formats of secret names:
    - Full path: "projects/project-id/secrets/SECRET_NAME"
    - Already extracted: "SECRET_NAME"

    Args:
        secret_name: The secret name or path

    Returns:
        str: The extracted secret name without project prefix
    """
    if "/secrets/" in secret_name:
        return secret_name.split("/secrets/")[-1]
    return secret_name


def _get_secret_url(secret_name: str, gcp_project_id: str) -> str:
    """Generate a URL for a secret in the GCP Secret Manager console.

    Note: This URL itself does not contain secrets or sensitive information.
    The URL itself is only useful for valid logged-in users of the project, and it
    safe to print this URL in logs.

    Args:
        secret_name: The name of the secret in GCP.
        gcp_project_id: The GCP project ID.

    Returns:
        str: URL to the secret in the GCP console
    """
    # Ensure we have just the secret name without the project prefix
    secret_name = _extract_secret_name(secret_name)
    return f"https://console.cloud.google.com/security/secret-manager/secret/{secret_name}/versions?hl=en&project={gcp_project_id}"


def _fetch_secret_handles(
    connector_name: str,
    gcp_project_id: str = GCP_PROJECT_ID,
) -> list["Secret"]:  # type: ignore
    """Fetch secrets from Google Secret Manager."""
    if not secretmanager:
        raise ImportError(
            "google-cloud-secret-manager package is required for Secret Manager integration. "
            "Install it with 'pip install airbyte-cdk[dev]' "
            "or 'pip install google-cloud-secret-manager'."
        )

    client = _get_gsm_secrets_client()

    # List all secrets with the connector label
    parent = f"projects/{gcp_project_id}"
    filter_string = f"labels.{CONNECTOR_LABEL}={connector_name}"
    secrets = client.list_secrets(
        request=secretmanager.ListSecretsRequest(
            parent=parent,
            filter=filter_string,
        )
    )
    return [s for s in secrets]


def _write_secret_file(
    secret: "Secret",  # type: ignore
    client: "secretmanager.SecretManagerServiceClient",  # type: ignore
    file_path: Path,
    connector_name: str,
    gcp_project_id: str,
) -> None:
    """Write the most recent enabled version of a secret to a file.

    Lists all enabled versions of the secret and selects the most recent one.
    Raises ConnectorSecretWithNoValidVersionsError if no enabled versions are found.

    Args:
        secret: The secret to write to a file
        client: The Secret Manager client
        file_path: The path to write the secret to
        connector_name: The name of the connector
        gcp_project_id: The GCP project ID

    Raises:
        ConnectorSecretWithNoValidVersionsError: If no enabled version is found
    """
    # List all enabled versions of the secret.
    response = client.list_secret_versions(
        request={"parent": secret.name, "filter": "state:ENABLED"}
    )

    # The API returns versions pre-sorted in descending order, with the
    # 0th item being the latest version.
    versions = list(response)

    if not versions:
        secret_name = _extract_secret_name(secret.name)
        raise ConnectorSecretWithNoValidVersionsError(
            connector_name=connector_name,
            secret_name=secret_name,
            gcp_project_id=gcp_project_id,
        )

    enabled_version = versions[0]

    response = client.access_secret_version(name=enabled_version.name)
    file_path.write_text(response.payload.data.decode("UTF-8"))
    file_path.chmod(0o600)  # default to owner read/write only


def _get_secrets_dir(
    connector_directory: Path,
    connector_name: str,
    ensure_exists: bool = True,
) -> Path:
    _ = connector_name  # Unused, but it may be used in the future for logging
    secrets_dir = connector_directory / "secrets"
    if ensure_exists:
        secrets_dir.mkdir(parents=True, exist_ok=True)

        gitignore_path = secrets_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("*")

    return secrets_dir


def _get_secret_filepath(
    secrets_dir: Path,
    secret: Secret,  # type: ignore
) -> Path:
    """Get the file path for a secret based on its labels."""
    if secret.labels and "filename" in secret.labels:
        return secrets_dir / f"{secret.labels['filename']}.json"

    return secrets_dir / "config.json"  # Default filename


def _get_gsm_secrets_client() -> "secretmanager.SecretManagerServiceClient":  # type: ignore
    """Get the Google Secret Manager client."""
    if not secretmanager:
        raise ImportError(
            "google-cloud-secret-manager package is required for Secret Manager integration. "
            "Install it with 'pip install airbyte-cdk[dev]' "
            "or 'pip install google-cloud-secret-manager'."
        )

    credentials_json = os.environ.get("GCP_GSM_CREDENTIALS")
    if not credentials_json:
        raise ValueError(
            "No Google Cloud credentials found. "
            "Please set the `GCP_GSM_CREDENTIALS` environment variable."
        )

    return cast(
        "secretmanager.SecretManagerServiceClient",
        secretmanager.SecretManagerServiceClient.from_service_account_info(
            json.loads(credentials_json)
        ),
    )


def _print_ci_secrets_masks(
    secrets_dir: Path,
) -> None:
    """Print GitHub CI mask for secrets.

    https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#example-masking-an-environment-variable

    The env var `CI` is set to a truthy value in GitHub Actions, so we can use it to
    determine if we are in a CI environment. If not, we don't want to print the masks,
    as it will cause the secrets to be printed in clear text to STDOUT.
    """
    if not os.environ.get("CI", None):
        click.echo(
            "The `--print-ci-secrets-masks` option is only available in CI environments. "
            "The `CI` env var is either not set or not set to a truthy value. "
            "Skipping printing secret masks.",
            err=True,
        )
        return

    for secret_file_path in secrets_dir.glob("*.json"):
        config_dict = json.loads(secret_file_path.read_text())
        _print_ci_secrets_masks_for_config(config=config_dict)


def _print_ci_secret_mask_for_string(secret: str) -> None:
    """Print GitHub CI mask for a single secret string.

    We expect single-line secrets, but we also handle the case where the secret contains newlines.
    For multi-line secrets, we must print a secret mask for each line separately.
    """
    for line in secret.splitlines():
        if line.strip():  # Skip empty lines
            print(f"::add-mask::{line!s}")


def _print_ci_secret_mask_for_value(value: Any) -> None:
    """Print GitHub CI mask for a single secret value.

    Call this function for any values identified as secrets, regardless of type.
    """
    if isinstance(value, dict):
        # For nested dicts, we call recursively on each value
        for v in value.values():
            _print_ci_secret_mask_for_value(v)

        return

    if isinstance(value, list):
        # For lists, we call recursively on each list item
        for list_item in value:
            _print_ci_secret_mask_for_value(list_item)

        return

    # For any other types besides dict and list, we convert to string and mask each line
    # separately to handle multi-line secrets (e.g. private keys).
    for line in str(value).splitlines():
        if line.strip():  # Skip empty lines
            _print_ci_secret_mask_for_string(line)


def _print_ci_secrets_masks_for_config(
    config: dict[str, str] | list[Any] | Any,
) -> None:
    """Print GitHub CI mask for secrets config, navigating child nodes recursively."""
    if isinstance(config, list):
        # Check each item in the list to look for nested dicts that may contain secrets:
        for item in config:
            _print_ci_secrets_masks_for_config(item)

    elif isinstance(config, dict):
        for key, value in config.items():
            if _is_secret_property(key):
                logger.debug(f"Masking secret for config key: {key}")
                _print_ci_secret_mask_for_value(value)
            elif isinstance(value, (dict, list)):
                # Recursively check nested dicts and lists
                _print_ci_secrets_masks_for_config(value)


def _is_secret_property(property_name: str) -> bool:
    """Check if the property name is in the list of properties to mask.

    To avoid false negatives, we perform a case-insensitive check, and we include any property name
    that contains a rule entry, even if it is not an exact match.

    For example, if the rule entry is "password", we will also match "PASSWORD" and "my_password".
    """
    names_to_mask: list[str] = _get_spec_mask()
    if any([mask.lower() in property_name.lower() for mask in names_to_mask]):
        return True

    return False


@lru_cache
def _get_spec_mask() -> list[str]:
    """Get the list of properties to mask from the spec mask file."""
    response = requests.get(GLOBAL_MASK_KEYS_URL, allow_redirects=True)
    if not response.ok:
        logger.error(f"Failed to fetch spec mask: {response.content.decode('utf-8')}")
    try:
        return cast(list[str], yaml.safe_load(response.content)["properties"])
    except Exception as e:
        logger.error(f"Failed to parse spec mask: {e}")
        raise
