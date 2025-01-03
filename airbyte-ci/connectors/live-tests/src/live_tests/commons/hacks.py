# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy

import rich

console = rich.get_console()


def patch_configured_catalog(configured_catalog: dict) -> dict:
    """
    The configured catalog extracted from the platform can be incompatible with the airbyte-protocol.
    This leads to validation error when we serialize the configured catalog into a ConfiguredAirbyteCatalog object.
    This functions is a best effort to patch the configured catalog to make it compatible with the airbyte-protocol.
    """
    patched_catalog = copy.deepcopy(configured_catalog)
    for stream in patched_catalog["streams"]:
        if stream.get("destination_sync_mode") == "overwrite_dedup":
            stream["destination_sync_mode"] = "overwrite"
            console.log(
                f"Stream {stream['stream']['name']} destination_sync_mode has been patched from 'overwrite_dedup' to 'overwrite' to guarantee compatibility with the airbyte-protocol."
            )
    return patched_catalog
