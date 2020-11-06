"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Generator

from impala.dbapi import connect

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, Status, AirbyteStream
from base_python import AirbyteLogger, ConfigContainer, Source


def connecting(json_config):
    conn = connect(host=json_config["host"],
                   port=json_config["port"],
                   database=json_config["database"],
                   user=json_config["username"],
                   password=json_config["password"],
                   auth_mechanism=json_config["authMechanism"],
                   use_http_transport=True,
                   http_path="cliservice"
                   )
    cur = conn.cursor()
    return conn, cur


class SourceHive(Source):
    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        json_config = config_container.rendered_config
        try:
            logger.info("Hive Source: Start to connect to Hive server ......")
            conn, cur = connecting(json_config)
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
            logger.info("Hive Source: Connect successful! The Hive version is " + str(version))
            cur.close()
            conn.close()

        except Exception as e:
            logger.error("Hive Source: Connect failed! The reason is " + str(e))
            return AirbyteConnectionStatus(status=Status.FAILED)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        json_config = config_container.rendered_config
        logger.info("Hive source: Start to connect to Hive server ...... ")
        conn, cur = connecting(json_config)
        try:
            logger.info("Hive source: Start to query all tables from Hive server ...... ")
            cur.execute("show tables")
            tables = []
            for name in cur.fetchall():
                logger.info(f"Hive source: Contain table: {name[0]}")
                tables.append(name[0])

            streams = []
            for table_name in tables:
                metadata = []
                logger.info(f"Hive source: Start to query {table_name}'s metadata from Hive server ...... ")
                cur.execute(f"describe {table_name}")
                for column in cur.fetchall():
                    metadata.append(column)

                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {field[0]: {"type": field[1]} for field in metadata},
                }
                streams.append(AirbyteStream(name=table_name, json_schema=json_schema))
        except Exception as err:
            reason = f"Hive source: Failed to discover schemas"
            logger.error(reason)
            raise err
        cur.close()
        conn.close()
        return AirbyteCatalog(streams=streams)
