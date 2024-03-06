# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A simple test of AirbyteLib, using the PokeAPI source connector.

Usage (from airbyte-lib root directory):
> poetry run python ./examples/run_pokeapi.py

No setup is needed, but you may need to delete the .venv-source-pokeapi folder
if your installation gets interrupted or corrupted.
"""
from __future__ import annotations

import airbyte_lib as ab


source = ab.get_source(
    "source-pokeapi",
    config={"pokemon_name": "bulbasaur"},
    install_if_missing=True,
)
source.check()

# print(list(source.get_records("pokemon")))
source.read(cache=ab.new_local_cache("poke"))
