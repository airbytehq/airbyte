#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_pokeapi import SourcePokeapi


def run():
    source = SourcePokeapi()
    launch(source, sys.argv[1:])
