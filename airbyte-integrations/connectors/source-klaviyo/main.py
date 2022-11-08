#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_klaviyo import SourceKlaviyo

if __name__ == "__main__":
    source = SourceKlaviyo()
    launch(source, sys.argv[1:])
