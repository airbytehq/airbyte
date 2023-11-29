#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Mapping, Tuple, Any, List, Optional

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import AbstractSource
from source_netsuite_odbc.discover_utils import NetsuiteODBCTableDiscoverer
from source_netsuite_odbc.reader_utils import NetsuiteODBCTableReader, NETSUITE_PAGINATION_INTERVAL
from .streams import NetsuiteODBCStream
from .odbc_utils import NetsuiteODBCCursorConstructor



class SourceNetsuiteOdbc(AbstractSource):
    logger: logging.Logger = logging.getLogger("airbyte")
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        cursor_constructor = NetsuiteODBCCursorConstructor()
        discoverer = NetsuiteODBCTableDiscoverer(cursor_constructor.create_database_cursor(config))
        streams = discoverer.get_streams()
        stream_objects = []
        for stream in streams:
            stream_name = stream.name
            netsuite_stream = NetsuiteODBCStream(cursor=cursor_constructor.create_database_cursor(config), table_name=stream_name, stream=stream)
            stream_objects.append(netsuite_stream)
        return stream_objects
    
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param logger: source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.
        """
        try:
            cursor_constructor = NetsuiteODBCCursorConstructor()
            cursor = cursor_constructor.create_database_cursor(config)

            cursor.execute("SELECT * FROM OA_TABLES")
            row = cursor.fetchone()
            print(row)
            row = cursor.fetchone()
            print(row)

            cursor.execute("SELECT column_name, COUNT(*) FROM OA_COLUMNS WHERE oa_userdata LIKE '%M-%' GROUP BY column_name")
            while True:
                row = cursor.fetchone()
                if not row:
                    break
                print(row)
            return True, None
        except Exception as e:
            logger.error(e)
            return False, e

    def find_emitted_at(self):
        return int(datetime.now().timestamp()) * 1000


