#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import subprocess
from pathlib import Path
from typing import Any, List, Mapping

import jinja2
import requests


def readme_for_connector(name: str) -> str:
    """
    Generate a manifest-only README.md file for a connector using a Jinja2 template.
    """
    dir_path = Path(__file__).parent / "templates"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=str(dir_path)))
    template = env.get_template("README.md.j2")
    readme_name = name.replace("source-", "")
    rendered = template.render(source_name=readme_name)
    return rendered


def get_latest_base_image(image_name: str) -> str:
    """
    Fetch the latest base image from Docker Hub for a given image name.
    """
    base_url = "https://hub.docker.com/v2/repositories/"

    tags_url = f"{base_url}{image_name}/tags/?page_size=10&ordering=last_updated"
    response = requests.get(tags_url)
    if response.status_code != 200:
        raise requests.ConnectionError(f"Error fetching tags: {response.status_code}")

    tags_data = response.json()
    if not tags_data["results"]:
        raise ValueError("No tags found for the image")

    # iterate through the tags to find the latest one that doesn't contain "dev" or "latest"
    for tag in tags_data["results"]:
        if "dev" not in tag["name"] and "latest" not in tag["name"]:
            latest_tag = tag["name"]
            break

    if not latest_tag:
        raise ValueError("No valid tags found for the image")

    manifest_url = f"{base_url}{image_name}/tags/{latest_tag}"
    response = requests.get(manifest_url)
    if response.status_code != 200:
        raise requests.ConnectionError(f"Error fetching manifest: {response.status_code}")

    manifest_data = response.json()
    digest = manifest_data.get("digest")

    if not digest:
        raise ValueError("No digest found for the image")

    full_reference = f"docker.io/{image_name}:{latest_tag}@{digest}"
    return full_reference


def revert_connector_directory(directory: Path) -> None:
    """
    Revert changes to a connector directory to the state at the last commit.
    Used as a cleanup step in the manifest-only pipeline.
    """
    try:
        # Restore the directory to its state at the last commit
        subprocess.run(["git", "restore", directory], check=True)
        # Remove untracked files and directories
        subprocess.run(["git", "clean", "-fd", directory], check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess calls
        print(f"An error occurred while reverting changes: {str(e)}")


def remove_parameters_from_manifest(d: dict | List | Mapping[str, Any]) -> dict | List:
    """
    Takes a dictionary (or a list) of keys and removes all instances of the key "$parameters" from it.
    """
    if isinstance(d, dict) or isinstance(d, Mapping):
        return {k: remove_parameters_from_manifest(v) for k, v in d.items() if k != "$parameters"}
    elif isinstance(d, list):
        return [remove_parameters_from_manifest(item) for item in d]
    else:
        return d
