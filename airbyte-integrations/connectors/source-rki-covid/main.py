#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_rki_covid import SourceRkiCovid

if __name__ == "__main__":
    source = SourceRkiCovid()
    launch(source, sys.argv[1:])
