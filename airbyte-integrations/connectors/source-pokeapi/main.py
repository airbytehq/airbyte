#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_pokeapi import SourcePokeapi

if __name__ == "__main__":
    source = SourcePokeapi()
    launch(source, sys.argv[1:])
