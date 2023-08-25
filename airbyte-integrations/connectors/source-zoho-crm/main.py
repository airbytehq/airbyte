#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zoho_crm import SourceZohoCrm

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZohoCrm()
    launch(source, sys.argv[1:])
