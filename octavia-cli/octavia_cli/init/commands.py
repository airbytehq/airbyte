#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
from typing import Iterable, Tuple

import click

DIRECTORIES_TO_CREATE = {"connections", "destinations", "sources"}


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


@click.command(help="Initialize required directories for the project.")
def init():
    click.echo("🔨 - Initializing the project.")
    created_directories, not_created_directories = create_directories(DIRECTORIES_TO_CREATE)
    if created_directories:
        message = f"✅ - Created the following directories: {', '.join(created_directories)}."
        click.echo(click.style(message, fg="green"))
    if not_created_directories:
        message = f"❓ - Already existing directories: {', '.join(not_created_directories) }."
        click.echo(click.style(message, fg="yellow", bold=True))
