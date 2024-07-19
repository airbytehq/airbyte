# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import yaml

from dataclasses import dataclass


@dataclass
class Manifest:
    host: str
    manifest: dict

    @property
    def name(self) -> str:
        return self.host.split(".")[1]

    @property
    def dir_name(self) -> str:
        return f"source-{self.name}"

    @property
    def yaml_manifest(self) -> str:
        return yaml.dump(self.manifest)

    @property
    def manifest_filename(self) -> str:
        return f"{self.host}.yaml"
