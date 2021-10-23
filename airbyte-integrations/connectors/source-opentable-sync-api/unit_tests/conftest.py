#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json

from pytest import fixture


@fixture
def config():
    f = open("secrets/config.json", "r")
    return json.load(f)
