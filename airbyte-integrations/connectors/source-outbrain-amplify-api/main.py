#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_outbrain_amplify_api import SourceOutbrainAmplifyApi

if __name__ == "__main__":
    source = SourceOutbrainAmplifyApi()
    launch(source, sys.argv[1:])
