#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zoho_crm import SourceZohoCrm

if __name__ == "__main__":
    source = SourceZohoCrm()
    launch(source, sys.argv[1:])
