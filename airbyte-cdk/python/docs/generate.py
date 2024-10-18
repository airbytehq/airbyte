#!/usr/bin/env python3

# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Generate docs for all public modules in the Airbyte CDK and save them to docs/generated.

Usage:
    poetry run python docs/generate.py

Or with Poe-the-Poet:
    poe docs-generate
    poe docs-preview

"""

from __future__ import annotations

import pathlib
import shutil

import pdoc


def run() -> None:
    """Generate docs for all public modules in the Airbyte CDK and save them to docs/generated."""
    public_modules = [
        "airbyte_cdk",
        "airbyte_cdk.sources",
        "airbyte_cdk.sources.abstract_source",
        "airbyte_cdk.sources.config",
        "airbyte_cdk.sources.source",
    ]

    # recursively delete the docs/generated folder if it exists
    if pathlib.Path("docs/generated").exists():
        shutil.rmtree("docs/generated")

    pdoc.render.configure(
        template_directory="docs",
        show_source=True,
        search=True,
        logo="https://docs.airbyte.com/img/logo-dark.png",
        favicon="https://docs.airbyte.com/img/favicon.png",
        mermaid=True,
        docformat="google",
    )
    pdoc.pdoc(
        *public_modules,
        output_directory=pathlib.Path("docs/generated"),
    )


if __name__ == "__main__":
    run()
