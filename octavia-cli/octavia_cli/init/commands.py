#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from typing import Iterable, Tuple, Dict, Optional

import click
import yaml

from octavia_cli.base_commands import OctaviaCommand

DIRECTORIES_TO_CREATE = {"connections", "destinations", "sources"}
API_HEADERS_CONFIGURATION_FILE = "api_headers.yaml"
DEFAULT_API_HEADERS_FILE_CONTENT = """
headers:
  - name: "Content-Type"
    value: "application/json"
""".strip("\n")

AIRBYTE_HEADERS_FILE_PATH_ENV_VARIABLE_NAME = "AIRBYTE_HEADERS_FILE_PATH"


def create_api_headers_configuration_file() -> bool:
    if not os.path.isfile(API_HEADERS_CONFIGURATION_FILE):
        with open(API_HEADERS_CONFIGURATION_FILE, "w") as file:
            file.write(DEFAULT_API_HEADERS_FILE_CONTENT)
        return True
    return False


def create_directories(directories_to_create: Iterable[str]) -> Tuple[Iterable[str], Iterable[str]]:
    created_directories = []
    not_created_directories = []
    for directory in directories_to_create:
        try:
            os.mkdir(directory)
            created_directories.append(directory)
        except FileExistsError:
            not_created_directories.append(directory)
    return created_directories, not_created_directories


@click.command(cls=OctaviaCommand, help="Initialize required directories for the project.")
@click.pass_context
def init(ctx: click.Context):
    click.echo("🔨 - Initializing the project.")
    created_directories, not_created_directories = create_directories(DIRECTORIES_TO_CREATE)
    if created_directories:
        message = f"✅ - Created the following directories: {', '.join(created_directories)}."
        click.echo(click.style(message, fg="green"))
    if not_created_directories:
        message = f"❓ - Already existing directories: {', '.join(not_created_directories) }."
        click.echo(click.style(message, fg="yellow", bold=True))

    created_api_headers_file = create_api_headers_configuration_file()

    if created_api_headers_file:
        message = f"✅ - Created example application headers configuration file {API_HEADERS_CONFIGURATION_FILE}"
        click.echo(click.style(message, fg="green", bold=True))
    else:
        message = "❓ - Application headers file already exists, skipping"
        click.echo(click.style(message, fg="yellow", bold=True))
