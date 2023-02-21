#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.sources import GenericManifestDeclarativeSource

if __name__ == "__main__":
    source = GenericManifestDeclarativeSource()
    launch(source, sys.argv[1:])
