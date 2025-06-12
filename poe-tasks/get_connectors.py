#!/usr/bin/env -S uv run
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.


# /// script
# dependencies = [
#     "typer>=0.9.0",
#     "requests>=2.31.0",
#     "pyyaml>=6.0",
# ]
# ///

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set

import requests
import typer
import yaml


app = typer.Typer(help="Get Airbyte connectors with filtering and GitHub Actions matrix output")

DEFAULT_REGISTRY_URL = "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"


def get_all_connectors() -> List[str]:
    """Get all connector directories from airbyte-integrations/connectors/"""
    connectors_path = Path("airbyte-integrations/connectors")
    if not connectors_path.exists():
        typer.echo("Error: Must run from airbyte repository root", err=True)
        raise typer.Exit(1)

    connectors = []
    for item in connectors_path.iterdir():
        if item.is_dir() and (item.name.startswith("source-") or item.name.startswith("destination-")):
            connectors.append(item.name)

    return sorted(connectors)


def get_connector_language(connector_name: str) -> str:
    """Extract language from metadata.yaml tags"""
    metadata_path = Path(f"airbyte-integrations/connectors/{connector_name}/metadata.yaml")
    if not metadata_path.exists():
        return "unknown"

    try:
        with open(metadata_path) as f:
            metadata = yaml.safe_load(f)

        tags = metadata.get("data", {}).get("tags", [])
        for tag in tags:
            if tag.startswith("language:"):
                return tag.split(":", 1)[1]
        return "unknown"
    except Exception:
        return "unknown"


def get_certified_connectors(registry_path: str) -> Set[str]:
    """Get certified connectors from registry (local file or remote URL)"""
    try:
        if registry_path.startswith(("http://", "https://")):
            response = requests.get(registry_path, timeout=30)
            response.raise_for_status()
            registry = response.json()
        else:
            with open(registry_path) as f:
                registry = json.load(f)

        certified = set()

        for source in registry.get("sources", []):
            if source.get("supportLevel") == "certified":
                docker_repo = source.get("dockerRepository", "")
                if docker_repo.startswith("airbyte/"):
                    name = docker_repo.replace("airbyte/", "")
                    certified.add(name)

        for dest in registry.get("destinations", []):
            if dest.get("supportLevel") == "certified":
                docker_repo = dest.get("dockerRepository", "")
                if docker_repo.startswith("airbyte/"):
                    name = docker_repo.replace("airbyte/", "")
                    certified.add(name)

        return certified
    except Exception as e:
        typer.echo(f"Warning: Could not fetch certified connectors from {registry_path}: {e}", err=True)
        return set()


def get_modified_connectors(prev_commit: bool = False) -> List[str]:
    """Get modified connectors using git diff"""
    try:
        if prev_commit:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"], capture_output=True, text=True, check=True
            )
        else:
            upstream_check = subprocess.run(["git", "remote", "get-url", "upstream"], capture_output=True)
            remote = "upstream" if upstream_check.returncode == 0 else "origin"

            subprocess.run(["git", "fetch", "--quiet", remote, "master"], check=True)
            result = subprocess.run(["git", "diff", "--name-only", f"{remote}/master...HEAD"], capture_output=True, text=True, check=True)

        connectors = set()
        for line in result.stdout.strip().split("\n"):
            if line and line.startswith("airbyte-integrations/connectors/"):
                parts = line.split("/")
                if len(parts) >= 3:
                    connector = parts[2]
                    if connector.startswith(("source-", "destination-")):
                        connectors.add(connector)

        return sorted(connectors)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: Git command failed: {e}", err=True)
        raise typer.Exit(1)


def get_pr_modified_connectors() -> List[str]:
    """Get modified connectors from GitHub PR API"""
    if not all([os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY"), os.getenv("GITHUB_EVENT_PATH")]):
        typer.echo("Warning: GitHub API not available, falling back to git diff", err=True)
        return get_modified_connectors()

    try:
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if not event_path:
            typer.echo("Warning: GITHUB_EVENT_PATH not set, falling back to git diff", err=True)
            return get_modified_connectors()

        with open(event_path) as f:
            event = json.load(f)

        if "pull_request" not in event:
            typer.echo("Warning: Not a pull request event, falling back to git diff", err=True)
            return get_modified_connectors()

        pr_number = event["pull_request"]["number"]
        repo = os.getenv("GITHUB_REPOSITORY")
        token = os.getenv("GITHUB_TOKEN")

        headers = {"Authorization": f"token {token}"}
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

        connectors = set()
        page = 1

        while True:
            response = requests.get(f"{url}?page={page}&per_page=100", headers=headers, timeout=30)
            response.raise_for_status()

            files = response.json()
            if not files:
                break

            for file_info in files:
                filename = file_info["filename"]
                if filename.startswith("airbyte-integrations/connectors/"):
                    parts = filename.split("/")
                    if len(parts) >= 3:
                        connector = parts[2]
                        if connector.startswith(("source-", "destination-")):
                            connectors.add(connector)

            page += 1

        return sorted(connectors)
    except Exception as e:
        typer.echo(f"Warning: GitHub API failed: {e}", err=True)
        return get_modified_connectors()


def output_results(connectors: List[str], json_format: bool = False):
    """Output connector list in requested format"""
    if not json_format:
        for connector in connectors:
            print(connector)
        return

    if not connectors:
        print('{"include": [{"connector": "", "language": ""}]}')
        return

    matrix_items = []
    for connector in connectors:
        language = get_connector_language(connector)
        matrix_items.append({"connector": connector, "language": language})

    matrix = {"include": matrix_items}
    print(json.dumps(matrix))


@app.command()
def main(
    language: str = typer.Option("", "--language", help="Filter for connectors of specific language (e.g., java, python, manifest-only)"),
    exclude_language: str = typer.Option("", "--exclude-language", help="Exclude connectors of specific language (e.g., java, python, manifest-only)"),
    certified: bool = typer.Option(False, "--certified", help="Filter for certified connectors only"),
    modified: bool = typer.Option(False, "--modified", help="Filter for modified connectors only"),
    json: bool = typer.Option(False, "--json", help="Output in GitHub Actions matrix JSON format"),
    prev_commit: bool = typer.Option(False, "--prev-commit", help="Compare against previous commit"),
    registry: str = typer.Option(DEFAULT_REGISTRY_URL, "--registry", help="Registry path (local file or remote URL)"),
    include_connector_list: str = typer.Option("", "--include-connector-list", help="Comma-separated list of connectors to include (union with filtered results)"),
    override_connector_list: str = typer.Option("", "--override-connector-list", help="Comma-separated list of connectors to use instead of filtered results"),
):
    """Get Airbyte connectors with filtering and GitHub Actions matrix output."""

    if language and exclude_language:
        typer.echo("Error: --language and --exclude-language are mutually exclusive", err=True)
        raise typer.Exit(1)
    
    if include_connector_list and override_connector_list:
        typer.echo("Error: --include-connector-list and --override-connector-list are mutually exclusive", err=True)
        raise typer.Exit(1)

    if override_connector_list:
        connectors = [c.strip() for c in override_connector_list.split(",") if c.strip()]
    else:
        if modified:
            if os.getenv("GITHUB_ACTIONS") and os.getenv("GITHUB_EVENT_NAME") in ["pull_request", "pull_request_target"]:
                connectors = get_pr_modified_connectors()
            else:
                connectors = get_modified_connectors(prev_commit)
        else:
            connectors = get_all_connectors()

        if certified:
            certified_set = get_certified_connectors(registry)
            connectors = [c for c in connectors if c in certified_set]

        if language or exclude_language:
            filtered = []
            for connector in connectors:
                connector_language = get_connector_language(connector)

                if language and connector_language == language:
                    filtered.append(connector)
                elif exclude_language and connector_language != exclude_language:
                    filtered.append(connector)

            connectors = filtered

    if include_connector_list:
        include_list = [c.strip() for c in include_connector_list.split(",") if c.strip()]
        connectors = sorted(list(set(connectors + include_list)))

    output_results(connectors, json)


if __name__ == "__main__":
    app()
