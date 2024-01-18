# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from dataclasses import dataclass
from importlib import metadata

INFRA_SUPPORTED_DAGGER_VERSIONS = {
    "0.6.4",
    "0.9.5",
}


@dataclass
class CIRequirements:
    """
    A dataclass to store the CI requirements.
    It used to make airbyte-ci client define the CI runners it will run on.
    """

    dagger_version = metadata.version("dagger-io")

    def __post_init__(self) -> None:
        if self.dagger_version not in INFRA_SUPPORTED_DAGGER_VERSIONS:
            raise ValueError(
                f"Unsupported dagger version: {self.dagger_version}. " f"Supported versions are: {INFRA_SUPPORTED_DAGGER_VERSIONS}."
            )

    def to_json(self) -> str:
        return json.dumps(
            {
                "dagger_version": self.dagger_version,
            }
        )
