# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Mapping
from urllib.parse import urlparse

import dpath.util
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver


@dataclass
class Connector:
    # Stem of the filename, i.e. filename without the .yaml
    filename: str

    # Raw manifest dict, can contain refs
    raw_manifest: Mapping[str, Any]

    @property
    def name(self) -> str:
        return self.filename.split(".")[-2]

    @cached_property
    def hostname(self) -> str:
        """
        Returns the hostname that the first stream of this connector uses.
        """
        base_url = dpath.util.get(self.resolved_manifest, "/streams/0/retriever/requester/url_base")

        # No streams? Return filename stem and pray.
        if base_url is None:
            return self.filename

        hostname = urlparse(str(base_url)).hostname
        if hostname is None:
            raise ValueError(f"Failed to extract hostname from {base_url}")

        return hostname

    @cached_property
    def resolved_manifest(self) -> Mapping[str, Any]:
        """
        Resolves all the references and definitions in the source manifest and returns the fully resolved manifest.
        """
        try:
            resolved_source_config = ManifestReferenceResolver().preprocess_manifest(self.raw_manifest)
            return ManifestComponentTransformer().propagate_types_and_parameters("", resolved_source_config, {})
        except Exception as e:
            raise ValueError(f"Failed to resolve manifest for {self.filename}") from e

    @property
    def dir_name(self) -> str:
        return f"source-{self.name}"

    @property
    def manifest_filename(self) -> str:
        return f"{self.filename}.yaml"
