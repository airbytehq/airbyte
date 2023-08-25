#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_facebook_marketing import SourceFacebookMarketing

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceFacebookMarketing()
    launch(source, sys.argv[1:])
