#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.auth import NoAuth
from pytest import fixture


@fixture
def config():
    return {"start_date": "start_date", "authenticator": NoAuth}
