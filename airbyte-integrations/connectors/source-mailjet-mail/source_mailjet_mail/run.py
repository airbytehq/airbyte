#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailjet_mail import SourceMailjetMail


def run():
    source = SourceMailjetMail()
    launch(source, sys.argv[1:])
