#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from gevent import monkey
monkey.patch_all()

from airbyte_cdk.entrypoint import launch
from source_facebook_marketing import SourceFacebookMarketing


if __name__ == "__main__":
    source = SourceFacebookMarketing()
    launch(source, sys.argv[1:])
