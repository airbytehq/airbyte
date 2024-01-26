#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_outbrain_amplify import SourceOutbrainAmplify


def run():
    source = SourceOutbrainAmplify()
    launch(source, sys.argv[1:])
