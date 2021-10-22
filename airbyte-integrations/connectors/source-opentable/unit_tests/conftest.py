#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.auth import NoAuth
from pytest import fixture
import json


@fixture
def config():
    f = open("secrets/config.json", "r")
    return json.load(f)
