#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_survey_sparrow import SourceSurveySparrow


def run():
    source = SourceSurveySparrow()
    launch(source, sys.argv[1:])
