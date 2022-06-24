#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import importlib.resources as pkg_resources
import os
from pathlib import Path
from typing import Iterable, Tuple

import click
from octavia_cli.base_commands import OctaviaCommand

from . import example_files

DIRECTORIES_TO_CREATE = {"connections", "destinations", "sources"}
DEFAULT_API_HEADERS_FILE_CONTENT = pkg_resources.read_text(example_files, "example_api_http_headers.yaml")
API_HTTP_HEADERS_TARGET_PATH = Path("api_http_headers.yaml")


def create_api_headers_configuration_file() -> bool:
    if not API_HTTP_HEADERS_TARGET_PATH.is_file():
        with open(API_HTTP_HEADERS_TARGET_PATH, "w") as file:
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

    created_api_http_headers_file = create_api_headers_configuration_file()
    if created_api_http_headers_file:
        message = f"✅ - Created API HTTP headers file in {API_HTTP_HEADERS_TARGET_PATH}"
        click.echo(click.style(message, fg="green", bold=True))
    else:
        message = "❓ - API HTTP headers file already exists, skipping."
        click.echo(click.style(message, fg="yellow", bold=True))
