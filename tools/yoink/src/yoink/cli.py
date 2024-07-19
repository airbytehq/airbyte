# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import click
from pathlib import Path

from utils import write_connector_to_disc, csv_to_manifests


@click.command()
@click.option("--output-dir", help="Where to write the manifests", default="./data/out")
@click.option(
    "--csv-file", help="Path to the CSV file", default="./data/manifests-100.csv"
)
@click.option(
    "--yeet", help="Overwrite existing connectors", is_flag=True, default=False
)
def yoink(output_dir: str, csv_file: str, yeet: bool = False):
    click.echo("🤖 Yoinking initialized")
    manifests = csv_to_manifests(Path(csv_file))

    click.echo(
        f"📦 Found {len(manifests)} manifests: {', '.join([m.name for m in manifests])}"
    )

    for manifest in manifests:
        click.echo(
            f"✔︎ Initializing a connector for {manifest.name} in {output_dir}/conectors/{manifest.dir_name}"
        )
        write_connector_to_disc(
            output_dir=Path(output_dir), manifest=manifest, yeet=yeet
        )
