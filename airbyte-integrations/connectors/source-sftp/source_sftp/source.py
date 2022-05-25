#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging
import json
from typing import Any, Iterable, List, Mapping, Optional, Tuple

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .client import get_client
from .stream import SFTPIncrementalStream


class SourceSftp(AbstractSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        pattern = config.get("pattern")
        if pattern and 'xlsx' in pattern:
            sheet_list_input = config.get("sheet_list",None)
            stream_list = []

            if sheet_list_input:
                sheet_list = sheet_list_input.split(',')
                
                for sheet in sheet_list:
                    reader_config = config.get("reader_config","{}")
                    reader_config = json.loads(reader_config)
                    reader_config["sheet_name"] = sheet
                    config["reader_config"] = json.dumps(reader_config)

                    client = get_client(config)
                    stream_list.append(SFTPIncrementalStream(
                        client=client,
                        table_name=sheet,
                        start_date=config["start_date"],
                        prefix=config.get("prefix"),
                        pattern=config.get("pattern"),
                        location=config.get("location")
                    ))
                
            else:
                print(f"No sheet_list provided, get first sheet only")
                client = get_client(config)
                stream_list.append(SFTPIncrementalStream(
                    client=client,
                    table_name=config["table_name"],
                    start_date=config["start_date"],
                    prefix=config.get("prefix"),
                    pattern=config.get("pattern"),
                    location=config.get("location")
                ))
            return stream_list
            
        elif 'csv' in pattern:
            client = get_client(config)
            return [SFTPIncrementalStream(
                client=client,
                table_name=config["table_name"],
                start_date=config["start_date"],
                prefix=config.get("prefix"),
                pattern=config.get("pattern"),
                location=config.get("location")
            )]
        else:
            raise ValueError(f"Pattern in config does not indicate file type is csv or xlsx. Please check again")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            client = get_client(config)
            files = client.get_files(
                prefix=config.get("prefix"),
                search_pattern=config.get("pattern"),
                modified_since=SFTPIncrementalStream.parse_dttm(config.get("start_date"))
            )

            if not files:
                logger.warning("Could not find any file.")

            return (True, None)
        except Exception as exc:
            logger.exception(exc)
            return (False, exc)

    @staticmethod
    def selected_fields(catalog: ConfiguredAirbyteCatalog) -> Iterable:
        for configured_stream in catalog.streams:
            yield from configured_stream.stream.json_schema["properties"].keys()
