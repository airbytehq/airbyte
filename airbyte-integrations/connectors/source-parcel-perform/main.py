#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_parcel_perform import SourceParcelPerform

if __name__ == "__main__":
    source = SourceParcelPerform()
    launch(source, sys.argv[1:])
