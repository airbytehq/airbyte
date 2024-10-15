#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import getpass
import os
import uuid
from typing import List, Tuple

import dagger
from base_images import console, published_image


def get_credentials() -> Tuple[str, str]:
    """This function will prompt the user for docker credentials.
    If the user has set the DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables, it will use those instead.
    Returns:
        Tuple[str, str]: (username, password)
    """
    if os.environ.get("DOCKER_HUB_USERNAME") and os.environ.get("DOCKER_HUB_PASSWORD"):
        console.log("Using docker credentials from environment variables.")
        return os.environ["DOCKER_HUB_USERNAME"], os.environ["DOCKER_HUB_PASSWORD"]
    else:
        console.log("Please enter your docker credentials.")
        console.log("You can set them as environment variables to avoid being prompted again: DOCKER_HUB_USERNAME, DOCKER_HUB_PASSWORD")
        # Not using inquirer here because of the sensitive nature of the information
        docker_username = input("Dockerhub username: ")
        docker_password = getpass.getpass("Dockerhub Password: ")
        return docker_username, docker_password


class CraneClient:

    CRANE_IMAGE_ADDRESS = (
        "gcr.io/go-containerregistry/crane/debug:v0.15.1@sha256:f6ddf8e2c47df889e06e33c3e83b84251ac19c8728a670ff39f2ca9e90c4f905"
    )

    def __init__(self, dagger_client: dagger.Client, docker_credentials: Tuple[str, str]):
        self.docker_hub_username_secret = dagger_client.set_secret("DOCKER_HUB_USERNAME", docker_credentials[0])
        self.docker_hub_username_password = dagger_client.set_secret("DOCKER_HUB_PASSWORD", docker_credentials[1])

        self.bare_container = (
            dagger_client.container().from_(self.CRANE_IMAGE_ADDRESS)
            # We don't want to cache any subsequent commands that might run in this container
            # because we want to have fresh output data every time we run this command.
            .with_env_variable("CACHE_BUSTER", str(uuid.uuid4()))
        )

        self.authenticated_container = self.login()

    def login(self) -> dagger.Container:
        return (
            self.bare_container.with_secret_variable("DOCKER_HUB_USERNAME", self.docker_hub_username_secret)
            .with_secret_variable("DOCKER_HUB_PASSWORD", self.docker_hub_username_password)
            .with_exec(["sh", "-c", "crane auth login index.docker.io -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"])
        )

    async def digest(self, repository_and_tag: str) -> str:
        console.log(f"Fetching digest for {repository_and_tag}...")
        return (await self.authenticated_container.with_exec(["digest", repository_and_tag], use_entrypoint=True).stdout()).strip()

    async def ls(self, registry_name: str, repository_name: str) -> List[str]:
        repository_address = f"{registry_name}/{repository_name}"
        console.log(f"Fetching published images in {repository_address}...")
        try:
            crane_ls_output = await self.authenticated_container.with_exec(["ls", repository_address], use_entrypoint=True).stdout()
            return crane_ls_output.splitlines()
        except dagger.ExecError as exec_error:
            # When the repository does not exist, crane ls returns an error with NAME_UNKNOWN in the stderr.
            if "NAME_UNKNOWN" in exec_error.stderr:
                console.log(f"Repository {repository_address} does not exist. Returning an empty list.")
                return []
            else:
                raise exec_error


class RemoteRepository:
    def __init__(self, crane_client: CraneClient, registry_name: str, repository_name: str):
        self.crane_client = crane_client
        self.registry_name = registry_name
        self.repository_name = repository_name

    async def get_all_images(self) -> List[published_image.PublishedImage]:
        repository_address = f"{self.registry_name}/{self.repository_name}"
        all_tags = await self.crane_client.ls(self.registry_name, self.repository_name)
        # CraneClient ls lists the tags available for a repository, but not the digests.
        # We want the digest to uniquely identify the image, so we need to fetch it separately with `crane digest`
        available_addresses_without_digest = [f"{repository_address}:{tag}" for tag in all_tags]
        available_addresses_with_digest = []
        for address in available_addresses_without_digest:
            digest = await self.crane_client.digest(address)
            available_addresses_with_digest.append(f"{address}@{digest}")
        return [published_image.PublishedImage.from_address(address) for address in available_addresses_with_digest]
