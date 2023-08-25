#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture

from airbyte_cdk.sources.streams.http.auth import NoAuth


@fixture()
def config():
    return {"start_date": "start_date", "authenticator": NoAuth}
