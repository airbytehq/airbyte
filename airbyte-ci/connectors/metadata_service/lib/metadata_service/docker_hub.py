#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import time
from typing import Dict, Optional

import requests


def get_docker_hub_auth_token() -> str:
    docker_username = os.environ.get("DOCKER_HUB_USERNAME")
    docker_password = os.environ.get("DOCKER_HUB_PASSWORD")

    if not (docker_username and docker_password):
        raise ValueError("Please set the DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables.")

    auth_url = "https://hub.docker.com/v2/users/login/"
    auth_data = {"username": docker_username, "password": docker_password}
    response = requests.post(auth_url, json=auth_data)

    if response.status_code != 200:
        raise ValueError("Failed to authenticate with Docker Hub. Please check your credentials.")

    token = response.json().get("token")
    return token


def get_docker_hub_headers() -> Dict | None:
    if "DOCKER_HUB_USERNAME" not in os.environ or "DOCKER_HUB_PASSWORD" not in os.environ:
        # If the Docker Hub credentials are not provided, we can only anonymously call the Docker Hub API.
        # This will only work for public images and lead to a lower rate limit.
        return {}
    else:
        token = get_docker_hub_auth_token()
        return {"Authorization": f"JWT {token}"} if token else {}


def get_docker_hub_tags_and_digests(
    image_name: str,
    retries: int = 0,
    wait_sec: int = 30,
    next_page_url: str | None = None,
    tags_and_digests: Dict[str, str] | None = None,
    paginate: bool = True,
) -> Dict[str, str]:
    """Find all released tags and digests for an image.

    Args:
        image_name (str): The image name to get tags and digest
        retries (int, optional): The number of times to retry the request. Defaults to 0.
        wait_sec (int, optional): The number of seconds to wait between retries. Defaults to 30.
        next_page_url (str | None, optional): The next DockerHub page to consume. Defaults to None.
        tags_and_digest (Dict[str, str] | None, optional): The accumulated tags and digests for recursion. Defaults to None.

    Returns:
        Dict[str, str]: Mapping of image tag to digest
    """
    headers = get_docker_hub_headers()
    tags_and_digests = tags_and_digests or {}

    if not next_page_url:
        tags_url = f"https://registry.hub.docker.com/v2/repositories/{image_name}/tags"
    else:
        tags_url = next_page_url

    # Allow for retries as the DockerHub API is not always reliable with returning the latest publish.
    for _ in range(retries + 1):
        response = requests.get(tags_url, headers=headers)
        if response.ok:
            break

        # This is to handle the case when a connector has not ever been released yet.
        if response.status_code == 404:
            print(f"{tags_url} returned a 404. The connector might not be released yet.")
            print(response)
            return tags_and_digests
        time.sleep(wait_sec)

    response.raise_for_status()
    json_response = response.json()
    tags_and_digests.update({result["name"]: result.get("digest") for result in json_response.get("results", [])})
    if paginate:
        if next_page_url := json_response.get("next"):
            tags_and_digests.update(
                get_docker_hub_tags_and_digests(
                    image_name, retries=retries, wait_sec=wait_sec, next_page_url=next_page_url, tags_and_digests=tags_and_digests
                )
            )
    return tags_and_digests


def get_latest_version_on_dockerhub(image_name: str) -> str | None:
    tags_and_digests = get_docker_hub_tags_and_digests(image_name, retries=3, wait_sec=30)
    if latest_digest := tags_and_digests.get("latest"):
        for tag, digest in tags_and_digests.items():
            if digest == latest_digest and tag != "latest":
                return tag
    return None


def is_image_on_docker_hub(image_name: str, version: str, digest: Optional[str] = None, retries: int = 0, wait_sec: int = 30) -> bool:
    """Check if a given image and version exists on Docker Hub.

    Args:
        image_name (str): The name of the image to check.
        version (str): The version of the image to check.
        digest (str, optional): The digest of the image to check. Defaults to None.
        retries (int, optional): The number of times to retry the request. Defaults to 0.
        wait_sec (int, optional): The number of seconds to wait between retries. Defaults to 30.
    Returns:
        bool: True if the image and version exists on Docker Hub, False otherwise.
    """

    headers = get_docker_hub_headers()

    tag_url = f"https://registry.hub.docker.com/v2/repositories/{image_name}/tags/{version}"

    # Allow for retries as the DockerHub API is not always reliable with returning the latest publish.
    for _ in range(retries + 1):
        response = requests.get(tag_url, headers=headers)
        if response.ok:
            break
        time.sleep(wait_sec)

    if not response.ok:
        response.raise_for_status()
        return False

    # If a digest is provided, check that it matches the digest of the image on Docker Hub.
    if digest is not None:
        return f"sha256:{digest}" == response.json()["digest"]
    return True
