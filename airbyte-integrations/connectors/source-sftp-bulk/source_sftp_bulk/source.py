#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteStream, Status, SyncMode
from airbyte_cdk.sources import AbstractSource

from .client import SFTPClient
from .streams import FTPStream

logger = logging.getLogger("airbyte")


class SourceFtp(AbstractSource):
    @property
    def _default_json_schema(self):
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
        }

    def _generate_json_schema(self, dtypes: Dict[str, Any]) -> Dict[str, Any]:
        json_schema = self._default_json_schema

        for key, val in dtypes.items():
            if val == "int64":
                json_schema["properties"][key] = {"type": ["null", "integer"]}
            elif val == "float64":
                json_schema["properties"][key] = {"type": ["null", "number"]}
            elif val == "bool":
                json_schema["properties"][key] = {"type": ["null", "boolean"]}
            # Special case for last_modified timestamp
            elif key == "last_modified":
                json_schema["properties"][key] = {"type": ["null", "string"], "format": "date-time"}
            # Default to string
            else:
                json_schema["properties"][key] = {"type": ["null", "string"]}

        return json_schema

    def _infer_json_schema(self, config: Mapping[str, Any], connection: SFTPClient) -> Dict[str, Any]:
        file_pattern = config.get("file_pattern")
        files = connection.get_files(config["folder_path"], file_pattern)

        if len(files) == 0:
            logger.warning(f"No files found in folder {config['folder_path']} with pattern {file_pattern}")
            return self._default_json_schema

        # Get last file to infer schema
        # Use pandas `infer_objects` to infer dtypes
        df = connection.fetch_file(files[-1], config["file_type"])
        df = df.infer_objects()

        # Default column used for incremental sync
        # Contains the date when a file was last modified or added
        df["last_modified"] = files[-1]["last_modified"]

        if len(df) < 1:
            logger.warning(f"No records found in file {files[0]}, can't infer json schema")
            return self._default_json_schema

        return self._generate_json_schema(df.dtypes.to_dict())

    def _get_connection(self, config: Mapping[str, Any]) -> SFTPClient:
        return SFTPClient(
            host=config["host"],
            username=config["username"],
            password=config["password"],
            private_key=config.get("private_key", None),
            port=config["port"],
        )

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, AirbyteConnectionStatus]:
        try:
            conn = self._get_connection(config)
            conn._connect()
            conn.close()
            return (True, AirbyteConnectionStatus(status=Status.SUCCEEDED))
        except Exception as ex:
            logger.error(
                f"Failed to connect to FTP server: {ex}",
            )
            return (False, AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(ex)}"))

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        _, status = self.check_connection(logger, config)
        return status

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        conn = self._get_connection(config)
        json_schema = self._infer_json_schema(config, conn)

        stream_name = config["stream_name"]
        streams = []

        sync_modes = [SyncMode.full_refresh]

        file_most_recent = config.get("file_most_recent", False)
        if not file_most_recent:
            logger.debug("File most recent is false, enabling incremental sync mode")
            sync_modes.append(SyncMode.incremental)

        streams.append(
            AirbyteStream(
                name=stream_name,
                json_schema=json_schema,
                supported_sync_modes=sync_modes,
                source_defined_cursor=True,
                default_cursor_field=[] if file_most_recent else ["last_modified"],
            )
        )

        conn.close()
        return AirbyteCatalog(streams=streams)

    def streams(self, config: json) -> List[AirbyteStream]:
        conn = SFTPClient(
            host=config["host"],
            username=config["username"],
            password=config["password"],
            private_key=config.get("private_key", None),
            port=config["port"],
        )

        start_date = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None)
        json_schema = self._infer_json_schema(config, conn)

        return [FTPStream(config=config, start_date=start_date, connection=conn, json_schema=json_schema)]
