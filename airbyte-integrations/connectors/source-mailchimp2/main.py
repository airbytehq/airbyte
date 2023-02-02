#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailchimp2 import SourceMailchimp2

if __name__ == "__main__":
    source = SourceMailchimp2()
    launch(source, sys.argv[1:])
