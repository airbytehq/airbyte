#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream


@pytest.fixture
def catalog(request):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=request.param, json_schema={}),
                sync_mode="full_refresh",
                destination_sync_mode="append",
            )
        ]
    )
