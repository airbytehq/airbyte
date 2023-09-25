#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sap_hana import SourceSapHana

if __name__ == "__main__":
    source = SourceSapHana()
    launch(source, sys.argv[1:])
