#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from dataclasses import dataclass

import semver


@dataclass
class PublishedImage:
    registry: str
    repository: str
    tag: str
    sha: str

    @property
    def address(self) -> str:
        return f"{self.registry}/{self.repository}:{self.tag}@sha256:{self.sha}"

    @classmethod
    def from_address(cls, address: str) -> PublishedImage:
        """Creates a PublishedImage instance from a docker image address.
        A docker image address is a string of the form:
        registry/repository:tag@sha256:sha

        Args:
            address (str): _description_

        Returns:
            PublishedImage: _description_
        """
        parts = address.split("/")
        registry = parts.pop(0)
        without_registry = "/".join(parts)
        repository, tag, sha = without_registry.replace("@sha256", "").split(":")
        return cls(registry, repository, tag, sha)

    @property
    def name_with_tag(self) -> str:
        return f"{self.repository}:{self.tag}"

    @property
    def version(self) -> semver.VersionInfo:
        return semver.VersionInfo.parse(self.tag)
