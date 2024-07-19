# Copyright (c) 2024 Airbyte, Inc., all rights reserved
from __future__ import annotations

import csv
import json
from pathlib import Path

import click
import jinja2
import requests
from ruamel.yaml import YAML

from .models import ManifestRecord


def load_manifest_from_file(manifest_path: Path) -> ManifestRecord:
    "Loads a Manifest from a yaml file, assumes the filename is the host name."
    with open(manifest_path, "r") as f:
        return ManifestRecord(host=manifest_path.stem, manifest=YAML().load(f))


def csv_to_manifests(input_csv_path: Path) -> list[ManifestRecord]:
    "Reads a CSV from Metabase into a list of Manifests."
    with open(input_csv_path, "r") as f:
        reader = csv.DictReader(f)
        return [ManifestRecord(host=row["Host"], manifest=json.loads(row["manifest"])) for row in reader]


def metadata_for_manifest(manifest: ManifestRecord, base_image: str, version: str) -> dict:
    """
    Generate a metadata.yaml file for a given manifest.

    Args:
        manifest (ManifestRecord): The manifest to generate metadata for.
        base_image (str, optional): The base image to use.
        version (str, optional): The version of the connector.
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./templates"))
    template = env.get_template("metadata.yaml.j2")
    rendered = template.render(
        source_name=manifest.name,
        host=manifest.host,
        version=version,
        base_image=base_image,
    )
    return YAML().load(rendered)


def readme_for_connector(name: str) -> str:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./templates"))
    template = env.get_template("README.md.j2")
    rendered = template.render(source_name=name)
    return rendered


def docs_file_for_connector(manifest: ManifestRecord, metadata: dict) -> str:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./templates"))
    template = env.get_template("documentation.md.j2")
    rendered = template.render(manifest=manifest.manifest, source_name=manifest.name, metadata=metadata)
    return rendered


def write_connector_to_disk(connectors_dir: Path, docs_dir: Path, manifest: ManifestRecord, yeet: bool = False) -> bool:
    """
    Bootstraps a new connector from a given manifest row, and writes it to disk at desired path.
    """
    # Make a new directory for this connector
    connector_dir = connectors_dir / manifest.dir_name
    try:
        connector_dir.mkdir(parents=True, exist_ok=yeet)
    except FileExistsError:
        click.echo(f"⚠️  {connector_dir} already exists. Skipping. Use --yeet to overwrite.")
        return False

    if not docs_dir.exists():
        click.echo(f"⚠️ Docs directory {docs_dir} does not exist.")
        return False

    # Prepare required items: metadata, README, and the docs file.
    metadata = metadata_for_manifest(manifest, version="0.1.0", base_image="airbyte/source-declarative-manifest")
    readme = readme_for_connector(manifest.name)
    docs_file = docs_file_for_connector(manifest, metadata)
    docs_file_name = f"{manifest.name}.md"

    # Write everything to disk.
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.dump(metadata, connector_dir / "metadata.yaml")
    yaml.dump(manifest.manifest, connector_dir / "manifest.yaml")

    with open(connector_dir / "README.md", "w") as f:
        f.write(readme)

    with open(docs_dir / docs_file_name, "w") as f:
        f.write(docs_file)

    return True


def list_existing_connectors(connectors_path: Path) -> list[str]:
    "List the existing source connectors in the target directory directory. Used to find all existing connectors in airbyte-integrations/connectors."
    connectors = []

    for connector in connectors_path.iterdir():
        # List source connectors only.
        if connector.is_dir() and connector.name.startswith("source-"):
            connectors.append("-".join(connector.name.split("-")[1:]))

    return connectors


def get_latest_base_image(image_name: str) -> str:
    base_url = "https://hub.docker.com/v2/repositories/"

    tags_url = f"{base_url}{image_name}/tags/?page_size=2&ordering=last_updated"
    response = requests.get(tags_url)
    if response.status_code != 200:
        raise requests.ConnectionError(f"Error fetching tags: {response.status_code}")

    tags_data = response.json()
    if not tags_data["results"]:
        raise ValueError("No tags found for the image")

    # the latest tag (at 0) is always `latest`, but we want the versioned one.
    latest_tag = tags_data["results"][1]["name"]

    manifest_url = f"{base_url}{image_name}/tags/{latest_tag}"
    response = requests.get(manifest_url)
    if response.status_code != 200:
        raise requests.ConnectionError(f"Error fetching manifest: {response.status_code}")

    manifest_data = response.json()
    digest = manifest_data.get("digest")

    if not digest:
        raise ValueError("No digest found for the image")

    full_reference = f"{image_name}:{latest_tag}@{digest}"
    return full_reference
