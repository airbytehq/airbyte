#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_kapiche_export_api import SourceKapicheExportApi

if __name__ == "__main__":
    source = SourceKapicheExportApi()
    launch(source, sys.argv[1:])
