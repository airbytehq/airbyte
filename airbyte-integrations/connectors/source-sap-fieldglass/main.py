#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_sap_fieldglass import SourceSapFieldglass

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceSapFieldglass()
    launch(source, sys.argv[1:])
