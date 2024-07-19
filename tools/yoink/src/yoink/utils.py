# Copyright (c) 2024 Airbyte, Inc., all rights reserved


import csv
import json
import pathlib

import click
import jinja2
import yaml
from models import Manifest


def load_manifest_from_file(manifest_path: pathlib.Path) -> Manifest:
    "Loads a Manifest from a yaml file"
    with open(manifest_path, "r") as f:
        return Manifest(host=manifest_path.stem, manifest=yaml.safe_load(f))


def csv_to_manifests(input_csv_path: pathlib.Path) -> list[Manifest]:
    "Reads a CSV from Metabase into a list of Manifests."
    with open(input_csv_path, "r") as f:
        reader = csv.DictReader(f)
        return [
            Manifest(host=row["Host"], manifest=json.loads(row["manifest"]))
            for row in reader
        ]


def metadata_for_manifest(manifest: Manifest) -> dict:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./templates"))
    template = env.get_template("metadata.yaml.j2")
    rendered = template.render(
        source_name=manifest.name, host=manifest.host, version="0.0.1"
    )
    return yaml.safe_load(rendered)


def write_connector_to_disc(
    output_dir: pathlib.Path, manifest: Manifest, yeet: bool = False
) -> bool:
    metadata = metadata_for_manifest(manifest)

    # Make a new directory for this connector
    connector_dir = output_dir / "connectors" / manifest.dir_name
    try:
        connector_dir.mkdir(parents=True, exist_ok=yeet)
    except FileExistsError:
        click.echo(
            f"⚠️  {connector_dir} already exists. Skipping. Use --yeet to overwrite."
        )
        return False

    with open(connector_dir / "metadata.yaml", "w") as f:
        f.write(yaml.dump(metadata))

    with open(connector_dir / "manifest.yaml", "w") as f:
        f.write(manifest.yaml_manifest)

    return True


def list_existing_connectors() -> list[str]:
    "List the existing connectors in the airbyte-integrations/connectors directory"
    connectors_dir = pathlib.Path("../../airbyte-integrations/connectors")
    connectors = []

    for connector in connectors_dir.iterdir():
        if connector.is_dir() and connector.name.startswith("source-"):
            connectors.append("-".join(connector.name.split("-")[1:]))

    return connectors
