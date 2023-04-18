#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from dataclasses import dataclass
from typing import List

from google.cloud import storage

SPEC_CACHE_BUCKET_NAME = "io-airbyte-cloud-spec-cache"
CACHE_FOLDER = "specs"
SPEC_FILE_NAME = "spec.json"


@dataclass
class CachedSpec:
    docker_repository: str
    docker_image_tag: str
    spec_cache_path: str


def get_spec_cache_path(docker_repository: str, docker_image_tag: str) -> str:
    """Returns the path to the spec.json file in the spec cache bucket."""
    return f"{CACHE_FOLDER}/{docker_repository}/{docker_image_tag}/{SPEC_FILE_NAME}"


def get_docker_info_from_spec_cache_path(spec_cache_path: str) -> CachedSpec:
    """Returns the docker repository and tag from the spec cache path."""

    # remove the leading "specs/" from the path using CACHE_FOLDER
    without_folder = spec_cache_path.replace(f"{CACHE_FOLDER}/", "")
    without_file = without_folder.replace(f"/{SPEC_FILE_NAME}", "")

    # split on only the last "/" to get the docker repository and tag
    # this is because the docker repository can have "/" in it
    docker_image_tag = without_file.split("/")[-1]
    docker_repository = without_file.replace(f"/{docker_image_tag}", "")

    return CachedSpec(
        docker_repository=docker_repository,
        docker_image_tag=docker_image_tag,
        spec_cache_path=spec_cache_path,
    )


def is_spec_cached(docker_repository: str, docker_image_tag: str) -> bool:
    """Returns True if the spec.json file exists in the spec cache bucket."""
    spec_path = get_spec_cache_path(docker_repository, docker_image_tag)

    client = storage.Client.create_anonymous_client()
    bucket = client.bucket(SPEC_CACHE_BUCKET_NAME)
    blob = bucket.blob(spec_path)

    return blob.exists()


def list_cached_specs() -> List[CachedSpec]:
    """Returns a list of all the specs in the spec cache bucket."""
    client = storage.Client.create_anonymous_client()
    bucket = client.bucket(SPEC_CACHE_BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=CACHE_FOLDER)

    return [get_docker_info_from_spec_cache_path(blob.name) for blob in blobs]


def get_cached_spec(spec_cache_path: str) -> dict:
    client = storage.Client.create_anonymous_client()
    bucket = client.bucket(SPEC_CACHE_BUCKET_NAME)
    return json.loads(bucket.blob(spec_cache_path).download_as_string())
