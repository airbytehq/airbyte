import os
import requests
from typing import List


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


def get_image_tags(repo: str, image: str) -> List[str]:
    token = get_docker_hub_auth_token()
    headers = {"Authorization": f"JWT {token}"}

    tags_url = f"https://hub.docker.com/v2/repositories/{repo}/{image}/tags/"
    params = {"page_size": 100}
    tags = []

    while True:
        response = requests.get(tags_url, headers=headers, params=params)
        if response.status_code != 200:
            raise ValueError("Failed to fetch image tags from Docker Hub.")

        data = response.json()
        tags.extend([result["name"] for result in data.get("results", [])])

        if data.get("next"):
            tags_url = data["next"]
        else:
            break

    return tags


def is_image_on_docker_hub(image_name: str, version: str) -> bool:
    """Check if a given image and version exists on Docker Hub.

    Args:
        image_name (str): The name of the image to check.
        version (str): The version of the image to check.

    Returns:
        bool: True if the image and version exists on Docker Hub, False otherwise.
    """
    repo, image = image_name.split("/")
    tags = get_image_tags(repo, image)

    return version in tags
