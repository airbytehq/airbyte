#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_surveymonkey import MigrateAccessTokenToCredentials, SourceSurveymonkey


def run():
    source = SourceSurveymonkey()
    MigrateAccessTokenToCredentials.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
