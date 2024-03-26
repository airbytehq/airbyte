# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from dataclasses import dataclass
from importlib import metadata


@dataclass
class CIRequirements:
    """
    A dataclass to store the CI requirements.
    It used to make airbyte-ci client define the CI runners it will run on.
    """

    dagger_version = metadata.version("dagger-io")

    @property
    def dagger_engine_image(self) -> str:
        return f"registry.dagger.io/engine:v{self.dagger_version}"

    def to_json(self) -> str:
        return json.dumps(
            {
                "dagger_version": self.dagger_version,
                "dagger_engine_image": self.dagger_engine_image,
            }
        )
