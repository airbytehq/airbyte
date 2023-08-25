#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_rki_covid import SourceRkiCovid

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceRkiCovid()
    launch(source, sys.argv[1:])
