#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def test_config():
    return {
        "merchant_id": "mech_id",
        "public_key": "pub_key",
        "start_date": "2020-11-22T20:32:05Z",
        "private_key": "p k",
        "environment": "Sandbox",
    }
