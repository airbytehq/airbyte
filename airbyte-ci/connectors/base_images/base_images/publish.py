#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
import sys
from typing import Optional, Tuple, Type

import anyio
import dagger
import inquirer  # type: ignore
import semver
from base_images import common, console, consts, errors, hacks, registries


async def publish_variants_to_remote(
    version: semver.VersionInfo, BaseImageClass: Type[common.AirbyteConnectorBaseImage]
) -> Tuple[Optional[common.PublishedDockerImage], Optional[str]]:
    """
    Publishes a new version of a base image to the remote registry.
    """
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        base_image_version = BaseImageClass(dagger_client, version)
        address = f"{consts.REMOTE_REGISTRY}/{base_image_version.image_name}:{base_image_version.version}"
        variants_to_publish = []
        for platform in consts.PLATFORMS_WE_PUBLISH_FOR:
            try:
                await base_image_version.run_sanity_checks(platform)
            except errors.SanityCheckError as e:
                console.log(f"Sanity checks failed for {platform}: {e}")
                return None, None
            console.log(f"Sanity checks passed for {platform}")
            variants_to_publish.append(base_image_version.get_container(platform))
        example_dockerfile = hacks.get_container_dockerfile(variants_to_publish[0])
        published_docker_image = None
        confirm_answer = inquirer.prompt([inquirer.Confirm("confirm_publishing", message=f"Do you really want to publish {address}?")])
        if confirm_answer["confirm_publishing"]:
            console.log(f"Publishing {address}")
            # Publish with forced compression to ensure backward compatibility with older versions of docker
            published_address = await variants_to_publish[0].publish(
                address, platform_variants=variants_to_publish[1:], forced_compression=dagger.ImageLayerCompression.Gzip
            )
            published_docker_image = common.PublishedDockerImage.from_address(published_address)
        return published_docker_image, example_dockerfile


def main():

    select_base_image_class_answers = inquirer.prompt(
        [
            inquirer.List(
                "BaseImageClass",
                message="Which base image would you like to publish?",
                choices=[(BaseImageClass.image_name, BaseImageClass) for BaseImageClass in registries.MANAGED_BASE_IMAGES],
            )
        ]
    )
    BaseImageClass = select_base_image_class_answers["BaseImageClass"]
    registry = registries.VersionRegistry.load_from_disk(BaseImageClass)
    latest_version = registry.latest_version or semver.VersionInfo.parse("0.0.0")

    new_version_answers = inquirer.prompt(
        [
            inquirer.List(
                "new_version",
                message="Which kind of new version would you like to cut?",
                choices=[
                    ("prerelease", latest_version.bump_prerelease()),
                    ("patch", latest_version.bump_patch()),
                    ("minor", latest_version.bump_minor()),
                    ("major", latest_version.bump_major()),
                ],
            ),
            inquirer.Text("changelog_entry", message="What should the changelog entry be?"),
        ]
    )
    new_version, changelog_entry = new_version_answers["new_version"], new_version_answers["changelog_entry"]
    published_image, example_dockerfile = anyio.run(publish_variants_to_remote, new_version, BaseImageClass)
    if published_image is None:
        console.log("Publishing was aborted.")
        sys.exit(1)
    console.log(f"Published {published_image.address} successfully. Adding it to the registry.")
    example_dockerfile = example_dockerfile or ""
    new_registry_entry = registries.RegistryEntry(
        published_image, changelog_entry, example_dockerfile, datetime.datetime.utcnow(), new_version
    )
    registry.add_entry(new_registry_entry)
    registry.save()
    console.log(f"Added {published_image.address} to the registry.")
    console.log("Please update the docs: poetry run generate_docs")
