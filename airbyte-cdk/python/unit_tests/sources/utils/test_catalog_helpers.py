#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, SyncMode
from airbyte_cdk.sources.utils.catalog_helpers import CatalogHelper


def test_coerce_catalog_as_full_refresh():
    incremental = AirbyteStream(
        name="1",
        json_schema={"k": "v"},
        supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        source_defined_cursor=True,
        default_cursor_field=["cursor"],
    )
    full_refresh = AirbyteStream(
        name="2", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False
    )
    input = AirbyteCatalog(streams=[incremental, full_refresh])

    expected = AirbyteCatalog(
        streams=[
            AirbyteStream(name="1", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=False),
            full_refresh,
        ]
    )

    assert CatalogHelper.coerce_catalog_as_full_refresh(input) == expected
