#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_kustomer_singer import SourceKustomerSinger

if __name__ == "__main__":
    source = SourceKustomerSinger()
    launch(source, sys.argv[1:])
