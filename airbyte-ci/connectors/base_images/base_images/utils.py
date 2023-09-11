#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path
from typing import Type

from base_images import common
from py_markdown_table.markdown_table import markdown_table


def write_changelog_file(
    changelog_path: Path, base_cls: Type[common.AirbyteConnectorBaseImage], base_images: dict[str, Type[common.AirbyteConnectorBaseImage]]
):
    def get_version_with_link_md(cls: Type[common.AirbyteConnectorBaseImage]) -> str:
        return f"[{cls.version}]({cls.github_url})"

    entries = [
        {
            "Version": get_version_with_link_md(base_cls),
            "Changelog": base_cls.changelog,
        }
        for _, base_cls in base_images.items()
    ]
    markdown = markdown_table(entries).set_params(row_sep="markdown", quote=False).get_markdown()
    with open(changelog_path, "w") as f:
        f.write(f"# Changelog for {base_cls.image_name}\n\n")
        f.write(markdown)
