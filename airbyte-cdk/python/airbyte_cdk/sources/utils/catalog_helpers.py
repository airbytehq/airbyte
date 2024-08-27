#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from copy import copy

from airbyte_cdk.models import AirbyteCatalog, AirbyteCatalogSerializer, SyncMode


class CatalogHelper:
    @staticmethod
    def coerce_catalog_as_full_refresh(catalog: AirbyteCatalog) -> AirbyteCatalog:
        """
        Updates the sync mode on all streams in this catalog to be full refresh
        """
        for stream in catalog.streams:
            stream.source_defined_cursor = False
            stream.supported_sync_modes = [SyncMode.full_refresh]
            stream.default_cursor_field = None

        return catalog
