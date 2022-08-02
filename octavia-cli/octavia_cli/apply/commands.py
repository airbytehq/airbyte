#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from glob import glob
from typing import List, Optional, Tuple

import airbyte_api_client
import click
from octavia_cli.base_commands import OctaviaCommand
from octavia_cli.check_context import REQUIRED_PROJECT_DIRECTORIES, requires_init

from .diff_helpers import display_diff_line
from .resources import BaseResource
from .resources import factory as resource_factory


@click.command(cls=OctaviaCommand, name="apply", help="Create or update Airbyte remote resources according local YAML configurations.")
@click.option("--file", "-f", "configurations_files", type=click.Path(), multiple=True)
@click.option("--force", is_flag=True, default=False, help="Does not display the diff and updates without user prompt.")
@click.pass_context
@requires_init
def apply(ctx: click.Context, configurations_files: List[click.Path], force: bool):
    if not configurations_files:
        configurations_files = find_local_configuration_files()

    resources = get_resources_to_apply(configurations_files, ctx.obj["API_CLIENT"], ctx.obj["WORKSPACE_ID"])
    for resource in resources:
        apply_single_resource(resource, force)


def get_resources_to_apply(
    configuration_files: List[str], api_client: airbyte_api_client.ApiClient, workspace_id: str
) -> List[BaseResource]:
    """Create resource objects with factory and sort according to apply priority.

    Args:
        configuration_files (List[str]): List of YAML configuration files.
        api_client (airbyte_api_client.ApiClient): the Airbyte API client.
        workspace_id (str): current Airbyte workspace id.

    Returns:
        List[BaseResource]: Resources sorted according to their apply priority.
    """
    all_resources = [resource_factory(api_client, workspace_id, path) for path in configuration_files]
    return sorted(all_resources, key=lambda resource: resource.APPLY_PRIORITY)


def apply_single_resource(resource: BaseResource, force: bool) -> None:
    """Runs resource creation if it was not created, update it otherwise.

    Args:
        resource (BaseResource): The resource to apply.
        force (bool): Whether force mode is on.
    """
    if resource.was_created:
        click.echo(
            click.style(
                f"🐙 - {resource.resource_name} exists on your Airbyte instance according to your state file, let's check if we need to update it!",
                fg="yellow",
            )
        )
        messages = update_resource(resource, force)
    else:
        click.echo(click.style(f"🐙 - {resource.resource_name} does not exists on your Airbyte instance, let's create it!", fg="green"))
        messages = create_resource(resource)
    click.echo("\n".join(messages))


def should_update_resource(force: bool, user_validation: Optional[bool], local_file_changed: bool) -> Tuple[bool, str]:
    """Function to decide if the resource needs an update or not.

    Args:
        force (bool): Whether force mode is on.
        user_validation (bool): User validated the existing changes.
        local_file_changed (bool): Whether the local file describing the resource was modified.

    Returns:
        Tuple[bool, str]: Boolean to know if resource should be updated and string describing the update reason.
    """
    if force:
        should_update, update_reason = True, "🚨 - Running update because the force mode is activated."
    elif user_validation is True:
        should_update, update_reason = True, "🟢 - Running update because you validated the changes."
    elif user_validation is False:
        should_update, update_reason = False, "🔴 - Did not update because you refused the changes."
    elif user_validation is None and local_file_changed:
        should_update, update_reason = (
            True,
            "🟡 - Running update because a local file change was detected and a secret field might have been edited.",
        )
    else:
        should_update, update_reason = False, "😴 - Did not update because no change detected."
    return should_update, click.style(update_reason, fg="green")


def prompt_for_diff_validation(resource_name: str, diff: str) -> bool:
    """Display the diff to user and prompt them from validation.

    Args:
        resource_name (str): Name of the resource the diff was computed for.
        diff (str): The diff.

    Returns:
        bool: Whether user validated the diff.
    """
    if diff:
        click.echo(
            click.style("👀 - Here's the computed diff (🚨 remind that diff on secret fields are not displayed):", fg="magenta", bold=True)
        )
        for line in diff.split("\n"):
            display_diff_line(line)
        return click.confirm(click.style(f"❓ - Do you want to update {resource_name}?", bold=True))
    else:
        return False


def create_resource(resource: BaseResource) -> List[str]:
    """Run a resource creation.

    Args:
        resource (BaseResource): The resource to create.

    Returns:
        List[str]: Post create messages to display to standard output.
    """
    created_resource, state = resource.create()
    return [
        click.style(f"🎉 - Successfully created {created_resource.name} on your Airbyte instance!", fg="green", bold=True),
        click.style(f"💾 - New state for {created_resource.name} saved at {state.path}", fg="yellow"),
    ]


def update_resource(resource: BaseResource, force: bool) -> List[str]:
    """Run a resource update. Check if update is required and prompt for user diff validation if needed.

    Args:
        resource (BaseResource): Resource to update
        force (bool): Whether force mode is on.

    Returns:
        List[str]: Post update messages to display to standard output.
    """
    output_messages = []
    diff = resource.get_diff_with_remote_resource()
    user_validation = None
    if not force and diff:
        user_validation = prompt_for_diff_validation(resource.resource_name, diff)
    should_update, update_reason = should_update_resource(force, user_validation, resource.local_file_changed)
    click.echo(update_reason)

    if should_update:
        updated_resource, state = resource.update()
        output_messages.append(
            click.style(f"🎉 - Successfully updated {updated_resource.name} on your Airbyte instance!", fg="green", bold=True)
        )
        output_messages.append(click.style(f"💾 - New state for {updated_resource.name} stored at {state.path}.", fg="yellow"))
    return output_messages


def find_local_configuration_files() -> List[str]:
    """Discover local configuration files.

    Returns:
        List[str]: Paths to YAML configuration files.
    """
    configuration_files = []
    for resource_directory in REQUIRED_PROJECT_DIRECTORIES:
        configuration_files += glob(f"./{resource_directory}/**/configuration.yaml")
    if not configuration_files:
        click.echo(click.style("😒 - No YAML file found to run apply.", fg="red"))
    return configuration_files
