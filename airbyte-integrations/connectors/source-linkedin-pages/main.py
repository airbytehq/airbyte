#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_pages import SourceLinkedinPages

if __name__ == "__main__":
    source = SourceLinkedinPages()
    launch(source, sys.argv[1:])
