#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_outbrain_amplify import SourceOutbrainAmplify

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceOutbrainAmplify()
    launch(source, sys.argv[1:])
