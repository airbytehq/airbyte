# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import pathlib
import shutil

import pdoc


<<<<<<< HEAD
def run():
    """
    Generate docs for all public modules in airbyte_lib and save them to docs/generated.
    Public modules are:
    * The main airbyte_lib module
    * All directory modules in airbyte_lib that don't start with an underscore
=======
def run() -> None:
    """Generate docs for all public modules in airbyte_lib and save them to docs/generated.

    Public modules are:
    * The main airbyte_lib module
    * All directory modules in airbyte_lib that don't start with an underscore.
>>>>>>> origin/master
    """
    public_modules = ["airbyte_lib"]

    # recursively delete the docs/generated folder if it exists
<<<<<<< HEAD
    if os.path.exists("docs/generated"):
        shutil.rmtree("docs/generated")

    # determine all folders in airbyte_lib that don't start with an underscore and add them to public_modules
=======
    if pathlib.Path("docs/generated").exists():
        shutil.rmtree("docs/generated")

    # All folders in `airbyte_lib` that don't start with "_" are treated as public modules.
>>>>>>> origin/master
    for d in os.listdir("airbyte_lib"):
        dir_path = pathlib.Path(f"airbyte_lib/{d}")
        if dir_path.is_dir() and not d.startswith("_"):
            public_modules.append(dir_path)

    pdoc.render.configure(template_directory="docs", show_source=False, search=False)
    pdoc.pdoc(*public_modules, output_directory=pathlib.Path("docs/generated"))
