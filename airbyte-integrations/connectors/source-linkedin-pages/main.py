#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_linkedin_pages import SourceLinkedinPages

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceLinkedinPages()
    launch(source, sys.argv[1:])
