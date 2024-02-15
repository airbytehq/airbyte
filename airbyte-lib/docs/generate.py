# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import os
import pathlib
import shutil

import pdoc

import airbyte_lib as ab

import typing

typing.TYPE_CHECKING = True


def run() -> None:
    """Generate docs for all public modules in airbyte_lib and save them to docs/generated.

    Public modules are:
    * The main airbyte_lib module
    * All directory modules in airbyte_lib that don't start with an underscore.
    """
    public_modules = ["airbyte_lib"]

    # recursively delete the docs/generated folder if it exists
    if pathlib.Path("docs/generated").exists():
        shutil.rmtree("docs/generated")

    # All files and folders in `airbyte_lib` that don't start with "_" are treated as public.
    for submodule in os.listdir("airbyte_lib"):
        submodule_path = pathlib.Path(f"airbyte_lib/{submodule}")
        if not submodule.startswith("_"):
            public_modules.append(submodule_path)

    pdoc.render.configure(
        template_directory="docs",
        show_source=False,
        search=False,
    )
    pdoc.pdoc(
        *public_modules,
        output_directory=pathlib.Path("docs/generated"),
    )
