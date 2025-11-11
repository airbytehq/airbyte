# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Generate OpenAPI command for the manifest server CLI."""

from pathlib import Path

import rich_click as click
from yaml import dump

from ._common import check_manifest_server_dependencies


@click.command("generate-openapi")
@click.option(
    "--output",
    "-o",
    default="airbyte_cdk/manifest_server/openapi.yaml",
    help="Output path for the OpenAPI YAML file",
    show_default=True,
)
def generate_openapi(output: str) -> None:
    """Generate OpenAPI YAML specification for the manifest server."""
    check_manifest_server_dependencies()

    # Import the FastAPI app
    from airbyte_cdk.manifest_server.app import app

    # Get OpenAPI schema
    openapi_schema = app.openapi()

    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write YAML file with header comment
    with open(output_path, "w") as f:
        f.write("# This file is auto-generated. Do not edit manually.\n")
        f.write("# To regenerate, run: manifest-server generate-openapi\n")
        f.write("\n")
        dump(openapi_schema, f, default_flow_style=False, sort_keys=False)

    click.echo(f"✅ OpenAPI YAML generated at: {output_path}")
    click.echo(f"   Title: {openapi_schema.get('info', {}).get('title', 'N/A')}")
    click.echo(f"   Version: {openapi_schema.get('info', {}).get('version', 'N/A')}")
