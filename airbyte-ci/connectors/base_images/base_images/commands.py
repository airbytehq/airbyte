#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import sys
from typing import Callable, Type

import anyio
import dagger
import inquirer  # type: ignore
import semver
from jinja2 import Environment, FileSystemLoader

from base_images import bases, console, consts, errors, hacks, publish, utils, version_registry


async def _generate_docs(dagger_client: dagger.Client):
    """This function will generate the README.md file from the templates/README.md.j2 template.
    It will first load all the registries to render the template with up to date information.
    """
    docker_credentials = utils.docker.get_credentials()
    env = Environment(loader=FileSystemLoader("base_images/templates"))
    template = env.get_template("README.md.j2")
    rendered_template = template.render({"registries": await version_registry.get_all_registries(dagger_client, docker_credentials)})
    with open("README.md", "w") as readme:
        readme.write(rendered_template)
    console.log("README.md generated successfully.")


async def _generate_release(dagger_client: dagger.Client):
    """This function will cut a new version on top of the previous one. It will prompt the user for release details: version bump, changelog entry.
    The user can optionally publish the new version to our remote registry.
    If the version is not published its changelog entry is still persisted.
    It can later be published by running the publish command.
    In the future we might only allow publishing new pre-release versions from this flow.
    """
    docker_credentials = utils.docker.get_credentials()
    select_base_image_class_answers = inquirer.prompt(
        [
            inquirer.List(
                "BaseImageClass",
                message="Which base image would you like to release a new version for?",
                choices=[(BaseImageClass.repository, BaseImageClass) for BaseImageClass in version_registry.MANAGED_BASE_IMAGES],
            )
        ]
    )
    BaseImageClass = select_base_image_class_answers["BaseImageClass"]
    registry = await version_registry.VersionRegistry.load(BaseImageClass, dagger_client, docker_credentials)
    latest_entry = registry.latest_entry

    # If theres in no latest entry, it means we have no version yet: the registry is empty
    # New version will be cut on top of 0.0.0 so this one will actually never be published
    seed_version = semver.VersionInfo.parse("0.0.0")
    if latest_entry is None:
        latest_version = seed_version
    else:
        latest_version = latest_entry.version

    if latest_version != seed_version and not latest_entry.published:  # type: ignore
        console.log(
            f"The latest version of {BaseImageClass.repository} ({latest_version}) has not been published yet. Please publish it first before cutting a new version."
        )
        sys.exit(1)

    new_version_answers = inquirer.prompt(
        [
            inquirer.List(
                "new_version",
                message=f"Which kind of new version would you like to cut? (latest version is {latest_version}))",
                choices=[
                    ("prerelease", latest_version.bump_prerelease()),
                    ("finalize", latest_version.finalize_version()),
                    ("patch", latest_version.bump_patch()),
                    ("patch-prerelease", latest_version.bump_patch().bump_prerelease()),
                    ("minor", latest_version.bump_minor()),
                    ("minor-prerelease", latest_version.bump_minor().bump_prerelease()),
                    ("major", latest_version.bump_major()),
                    ("major-prerelease", latest_version.bump_major().bump_prerelease()),
                ],
            ),
            inquirer.Text("changelog_entry", message="What should the changelog entry be?", validate=lambda _, entry: len(entry) > 0),
            inquirer.Confirm("publish_now", message="Would you like to publish it to our remote registry now?"),
        ]
    )

    new_version, changelog_entry, publish_now = (
        new_version_answers["new_version"],
        new_version_answers["changelog_entry"],
        new_version_answers["publish_now"],
    )

    base_image_version = BaseImageClass(dagger_client, new_version)

    try:
        await publish.run_sanity_checks(base_image_version)
        console.log("Sanity checks passed.")
    except errors.SanityCheckError as e:
        console.log(f"Sanity checks failed: {e}")
        console.log("Aborting.")
        sys.exit(1)
    dockerfile_example = hacks.get_container_dockerfile(base_image_version.get_container(consts.PLATFORMS_WE_PUBLISH_FOR[0]))

    # Add this step we can create a changelog entry: sanity checks passed, image built successfully and sanity checks passed.
    changelog_entry = version_registry.ChangelogEntry(new_version, changelog_entry, dockerfile_example)
    if publish_now:
        published_docker_image = await publish.publish_to_remote_registry(base_image_version)
        console.log(f"Published {published_docker_image.address} successfully.")
    else:
        published_docker_image = None
        console.log(
            f"Skipping publication. You can publish it later by running `poetry run publish {base_image_version.repository} {new_version}`."
        )

    new_registry_entry = version_registry.VersionRegistryEntry(published_docker_image, changelog_entry, new_version)
    registry.add_entry(new_registry_entry)
    console.log(f"Added {new_version} to the registry.")
    await _generate_docs(dagger_client)
    console.log("Generated docs successfully.")


async def _publish(
    dagger_client: dagger.Client, BaseImageClassToPublish: Type[bases.AirbyteConnectorBaseImage], version: semver.VersionInfo
):
    """This function will publish a specific version of a base image to our remote registry.
    Users are prompted for confirmation before overwriting an existing version.
    If the version does not exist in the registry, the flow is aborted and user is suggested to cut a new version first.
    """
    docker_credentials = utils.docker.get_credentials()
    registry = await version_registry.VersionRegistry.load(BaseImageClassToPublish, dagger_client, docker_credentials)
    registry_entry = registry.get_entry_for_version(version)
    if not registry_entry:
        console.log(f"No entry found for version {version} in the registry. Please cut a new version first: `poetry run generate-release`")
        sys.exit(1)
    if registry_entry.published:
        force_answers = inquirer.prompt(
            [
                inquirer.Confirm(
                    "force", message="This version has already been published to our remote registry. Would you like to overwrite it?"
                ),
            ]
        )
        if not force_answers["force"]:
            console.log("Not overwriting the already exiting image.")
            sys.exit(0)

    base_image_version = BaseImageClassToPublish(dagger_client, version)
    published_docker_image = await publish.publish_to_remote_registry(base_image_version)
    console.log(f"Published {published_docker_image.address} successfully.")
    await _generate_docs(dagger_client)
    console.log("Generated docs successfully.")


async def execute_async_command(command_fn: Callable, *args, **kwargs):
    """This is a helper function that will execute a command function in an async context, required by the use of Dagger."""
    # NOTE: Dagger logs using Rich now, and two rich apps don't play well with each other.
    # Logging into a file makes the CLI experience tolerable.
    async with dagger.Connection(dagger.Config(log_output=open("dagger.log", "w"))) as dagger_client:
        await command_fn(dagger_client, *args, **kwargs)


def generate_docs():
    """This command will generate the README.md file from the templates/README.md.j2 template.
    It will first load all the registries to render the template with up to date information.
    """
    anyio.run(execute_async_command, _generate_docs)


def generate_release():
    """This command will cut a new version on top of the previous one. It will prompt the user for release details: version bump, changelog entry.
    The user can optionally publish the new version to our remote registry.
    If the version is not published its changelog entry is still persisted.
    It can later be published by running the publish command.
    In the future we might only allow publishing new pre-release versions from this flow.
    """
    anyio.run(execute_async_command, _generate_release)


def publish_existing_version():
    """This command is intended to be used when:
    - We have a changelog entry for a new version but it's not published yet (for future publish on merge flows).
    - We have a good reason to overwrite an existing version in the remote registry.
    """
    parser = argparse.ArgumentParser(description="Publish a specific version of a base image to our remote registry.")
    parser.add_argument("repository", help="The base image repository name")
    parser.add_argument("version", help="The version to publish")
    args = parser.parse_args()

    version = semver.VersionInfo.parse(args.version)
    BaseImageClassToPublish = None
    for BaseImageClass in version_registry.MANAGED_BASE_IMAGES:
        if BaseImageClass.repository == args.repository:
            BaseImageClassToPublish = BaseImageClass
    if BaseImageClassToPublish is None:
        console.log(f"Unknown base image name: {args.repository}")
        sys.exit(1)

    anyio.run(execute_async_command, _publish, BaseImageClassToPublish, version)
