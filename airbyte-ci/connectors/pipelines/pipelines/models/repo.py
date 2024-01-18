# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Type
from urllib.parse import urlparse


class SupportedHosts(Enum):
    GITHUB = "github.com"


@dataclass
class Repo:
    name: str
    host: str

    @property
    def url(self) -> str:
        return f"https://{self.host}/{self.name}.git"

    @classmethod
    def from_url(cls: Type[Repo], repo_url: str) -> Repo:
        parsed_url = urlparse(repo_url)
        host = parsed_url.netloc
        if SupportedHosts(host) is SupportedHosts.GITHUB:
            repo_name = cls.get_github_repo_name(parsed_url.path)
            return Repo(name=repo_name, host=host)
        raise NotImplementedError("Only GitHub is supported for now")

    @classmethod
    def get_github_repo_name(cls: Type[Repo], url_path: str) -> str:
        # Remove leading slash and trailing .git
        return url_path[1:].split(".")[0]

    def __post_init__(self) -> None:
        # Validate the host is supported
        SupportedHosts(self.host)

    def __str__(self) -> str:
        return self.url
