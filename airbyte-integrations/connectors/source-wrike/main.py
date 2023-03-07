#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wrike import SourceWrike

if __name__ == "__main__":
    source = SourceWrike()
    launch(source, sys.argv[1:])
