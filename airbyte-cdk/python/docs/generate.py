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

import os
import pathlib
import shutil
from typing import cast

import pdoc


def run() -> None:
    """Generate docs for all public modules in the Airbyte CDK and save them to docs/generated."""

    public_modules = [
        "airbyte_cdk",
    ]

    # Walk all subdirectories and add them to the `public_modules` list
    # if they do not begin with a "_" character.
    for parent_dir, dirs, files in os.walk(pathlib.Path("airbyte_cdk")):
        for dir_name in dirs:
            if "/." in parent_dir or "/_" in parent_dir:
                continue

            if dir_name.startswith((".", "_")):
                continue

            print(f"Found module dir: {parent_dir + '|' + dir_name}")

            # Check if the directory name does not begin with a "_"
            module = (parent_dir + "." + dir_name).replace("/", ".")
            if "._" not in module and not module.startswith("_"):
                public_modules.append(module)

        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            if file_name in ["py.typed"]:
                continue
            if file_name.startswith((".", "_")):
                continue

            print(f"Found module file: {'|'.join([parent_dir, file_name])}")
            module = cast(str, ".".join([parent_dir, file_name])).replace("/", ".").removesuffix(".py")
            public_modules.append(module)

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
    nl = "\n"
    print(f"Generating docs for public modules: {nl.join(public_modules)}")
    pdoc.pdoc(
        *set(public_modules),
        output_directory=pathlib.Path("docs/generated"),
    )


if __name__ == "__main__":
    run()
