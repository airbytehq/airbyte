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


def is_image_on_docker_hub(image_name: str, version: str) -> bool:
    """Check if a given image and version exists on Docker Hub.

    Args:
        image_name (str): The name of the image to check.
        version (str): The version of the image to check.

    Returns:
        bool: True if the image and version exists on Docker Hub, False otherwise.
    """

    token = get_docker_hub_auth_token()
    headers = {"Authorization": f"JWT {token}"}
    tag_url = f"https://registry.hub.docker.com/v2/repositories/{image_name}/tags/{version}"
    response = requests.get(tag_url, headers=headers)

    return response.ok
