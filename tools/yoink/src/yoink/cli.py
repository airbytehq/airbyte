# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import sys
from pathlib import Path

import click
from ruamel.yaml import YAML

from .utils import (
    get_latest_base_image,
    load_connector_manifest_from_file,
    load_connectors_from_csv,
    metadata_for_connector,
    write_connector_to_disk,
)


@click.group()
def cli():
    pass


@cli.command(help="Yoink connector manifests from a CSV file and generate manifest-only connectors based on them.")
@click.option("--connectors-dir", help="Where to write the manifests", default="./data/out")
@click.option("--docs-dir", help="Where to write the docs", default="./data/out/docs")
@click.option("--csv-file", help="Path to the CSV file", default="./data/manifests-100.csv")
@click.option("--yeet", help="Overwrite existing connectors", is_flag=True, default=False)
def hoard(connectors_dir: str, docs_dir: str, csv_file: str, yeet: bool = False):
    click.echo("🤖 Yoinking initialized")
    manifests = load_connectors_from_csv(Path(csv_file))

    click.echo(f"📦 Found {len(manifests)} manifests: {', '.join([m.name for m in manifests])}")

    for manifest in manifests:
        click.echo(f"✔︎ Initializing a connector for {manifest.name} in {connectors_dir}/{manifest.dir_name}")
        write_connector_to_disk(connectors_dir=Path(connectors_dir) / "connectors", docs_dir=Path(docs_dir), connector=manifest, yeet=yeet)


@cli.command(help="Generate metadata for a given manifest file.")
@click.argument("manifest_path", type=Path)
@click.option(
    "--output-dir",
    help="Output directory. A connector directory (source-{name}) will be created in that dir.",
    default=Path("."),
    type=Path,
)
@click.option("--docs-dir", help="Where to write the docs", default="./docs", type=Path)
def shiny(manifest_path: Path, output_dir: Path, docs_dir: Path):
    if manifest_path.exists() is False:
        click.echo(f"❌ Manifest path {manifest_path} does not exist.")
        exit(1)

    if not output_dir.exists():
        click.echo(f"❌ Output directory {output_dir} does not exist.")
        exit(1)

    # Make a connector and write to disk. Always overwrite in bootstrap mode.
    manifest = load_connector_manifest_from_file(Path(manifest_path))
    if write_connector_to_disk(connector=manifest, connectors_dir=output_dir, docs_dir=docs_dir, yeet=True):
        click.echo(f"✅ Connector {manifest.name} has been written to disk!")
