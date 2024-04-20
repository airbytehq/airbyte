#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_rki_covid import SourceRkiCovid


def run():
    source = SourceRkiCovid()
    launch(source, sys.argv[1:])
