#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from enum import Enum
from typing import List

from google.cloud import storage

PROD_SPEC_CACHE_BUCKET_NAME = "io-airbyte-cloud-spec-cache"
CACHE_FOLDER = "specs"


class Registries(str, Enum):
    OSS = "oss"
    CLOUD = "cloud"

    @classmethod
    def _missing_(cls, value):
        """Returns the registry from the string value. (case insensitive)"""
        value = value.lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


SPEC_FILE_NAMES = {Registries.OSS: "spec.json", Registries.CLOUD: "spec.cloud.json"}


@dataclass
class CachedSpec:
    docker_repository: str
    docker_image_tag: str
    spec_cache_path: str
    registry: Registries

    def __str__(self) -> str:
        return self.spec_cache_path


def get_spec_file_name(registry: Registries) -> str:
    return SPEC_FILE_NAMES[registry]


def get_registry_from_spec_cache_path(spec_cache_path: str) -> Registries:
    """Returns the registry from the spec cache path."""
    for registry in Registries:
        file_name = get_spec_file_name(registry)
        if file_name in spec_cache_path:
            return registry

    raise Exception(f"Could not find any registry file name in spec cache path: {spec_cache_path}")


def get_docker_info_from_spec_cache_path(spec_cache_path: str) -> CachedSpec:
    """Returns the docker repository and tag from the spec cache path."""

    registry = get_registry_from_spec_cache_path(spec_cache_path)
    registry_file_name = get_spec_file_name(registry)

    # remove the leading "specs/" from the path using CACHE_FOLDER
    without_folder = spec_cache_path.replace(f"{CACHE_FOLDER}/", "")
    without_file = without_folder.replace(f"/{registry_file_name}", "")

    # split on only the last "/" to get the docker repository and tag
    # this is because the docker repository can have "/" in it
    docker_image_tag = without_file.split("/")[-1]
    docker_repository = without_file.replace(f"/{docker_image_tag}", "")

    return CachedSpec(
        docker_repository=docker_repository, docker_image_tag=docker_image_tag, spec_cache_path=spec_cache_path, registry=registry
    )


class SpecCache:
    def __init__(self, bucket_name: str = PROD_SPEC_CACHE_BUCKET_NAME):
        self.client = storage.Client.create_anonymous_client()
        self.bucket = self.client.bucket(bucket_name)
        self.cached_specs = self.get_all_cached_specs()

    def get_all_cached_specs(self) -> List[CachedSpec]:
        """Returns a list of all the specs in the spec cache bucket."""

        blobs = self.bucket.list_blobs(prefix=CACHE_FOLDER)

        return [get_docker_info_from_spec_cache_path(blob.name) for blob in blobs if blob.name.endswith(".json")]

    def _find_spec_cache(self, docker_repository: str, docker_image_tag: str, registry: Registries) -> CachedSpec:
        """Returns the spec cache path for a given docker repository and tag."""

        # find the spec cache path for the given docker repository and tag
        for cached_spec in self.cached_specs:
            if (
                cached_spec.docker_repository == docker_repository
                and cached_spec.registry == registry
                and cached_spec.docker_image_tag == docker_image_tag
            ):
                return cached_spec

        return None

    def find_spec_cache_with_fallback(self, docker_repository: str, docker_image_tag: str, registry_str: str) -> CachedSpec:
        """Returns the spec cache path for a given docker repository and tag and fallback to OSS if none found"""
        registry = Registries(registry_str)

        # if the registry is cloud try to return the cloud spec first
        if registry == Registries.CLOUD:
            spec_cache = self._find_spec_cache(docker_repository, docker_image_tag, registry)
            if spec_cache:
                return spec_cache

        # fallback to OSS
        return self._find_spec_cache(docker_repository, docker_image_tag, Registries.OSS)

    def download_spec(self, spec: CachedSpec) -> dict:
        """Downloads the spec from the spec cache bucket."""
        return json.loads(self.bucket.blob(spec.spec_cache_path).download_as_string())
