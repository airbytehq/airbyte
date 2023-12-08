#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_gcs import Config, Cursor, SourceGCS, SourceGCSStreamReader

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch

if __name__ == "__main__":
    _args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(_args)
    source = SourceGCS(SourceGCSStreamReader(), Config, catalog_path, cursor_cls=Cursor)
    launch(source, sys.argv[1:])
