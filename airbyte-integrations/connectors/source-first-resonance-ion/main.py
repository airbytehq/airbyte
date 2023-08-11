#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_first_resonance_ion import SourceFirstResonanceIon

if __name__ == "__main__":
    source = SourceFirstResonanceIon()
    launch(source, sys.argv[1:])
