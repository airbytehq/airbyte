#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dz_zoho_books import SourceDzZohoBooks

if __name__ == "__main__":
    source = SourceDzZohoBooks()
    launch(source, sys.argv[1:])
