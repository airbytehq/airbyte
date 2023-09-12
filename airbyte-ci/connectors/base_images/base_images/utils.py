#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares utility functions used by the base_images module.
"""

from pathlib import Path
from typing import Mapping, Type

from base_images import common
from py_markdown_table.markdown_table import markdown_table  # type: ignore


def write_changelog_file(changelog_path: Path, base_image_name: str, base_images: Mapping[str, Type[common.AirbyteConnectorBaseImage]]):
    """Writes the changelog file locally for a given base image. Per version entries are generated from the base_images Mapping.

    Args:
        changelog_path (Path): Local absolute path to the changelog file.
        base_image_name (str): The name of the base image e.g airbyte-python-connectors-base .
        base_images (Mapping[str, Type[common.AirbyteConnectorBaseImage]]): All the base images versions for a given base image.
    """

    def get_version_with_link_md(cls: Type[common.AirbyteConnectorBaseImage]) -> str:
        return f"[{cls.version}]({cls.github_url})"

    entries = [
        {
            "Version": get_version_with_link_md(base_cls),
            "Changelog": base_cls.changelog_entry,
        }
        for _, base_cls in base_images.items()
    ]
    markdown = markdown_table(entries).set_params(row_sep="markdown", quote=False).get_markdown()
    with open(changelog_path, "w") as f:
        f.write(f"# Changelog for {base_image_name}\n\n")
        f.write(markdown)
