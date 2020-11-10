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

from datetime import datetime
from typing import Generator

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, AirbyteRecordMessage, AirbyteStream, Status, Type
from base_python import AirbyteLogger, ConfigContainer, Source
from impala.dbapi import connect


def connect_to_hive(json_config):
    conn = connect(
        host=json_config["host"],
        port=json_config["port"],
        database=json_config["database"],
        user=json_config["username"],
        password=json_config["password"],
        auth_mechanism=json_config["authMechanism"],
        use_http_transport=True,
        http_path="cliservice",
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
            conn, cur = connect_to_hive(json_config)
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
            logger.info("Hive Source: Connect successful! The Hive version is " + str(version))

        except Exception as e:
            logger.error("Hive Source: Connect failed! The reason is " + str(e))
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")
        finally:
            cur.close()
            conn.close()
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        json_config = config_container.rendered_config
        logger.info("Hive source: Start to connect to Hive server ...... ")
        conn, cur = connect_to_hive(json_config)
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
            reason = "Hive source: Failed to discover schemas"
            logger.error(reason)
            raise err
        finally:
            cur.close()
            conn.close()
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config_container: ConfigContainer, catalog_path, state=None
    ) -> Generator[AirbyteMessage, None, None]:
        logger.info(f"Hive source: Reading catalog file({catalog_path}) from discover phase ...")
        catalog = AirbyteCatalog.parse_obj(self.read_config(catalog_path))
        tables = {}
        for stream in catalog.streams:
            columns = []
            for key in stream.json_schema["properties"].keys():
                columns.append(key)
            tables[stream.name] = columns

        json_config = config_container.rendered_config
        logger.info("Hive source: Start to connect to Hive server ...... ")
        conn, cur = connect_to_hive(json_config)
        logger.info("Hive source: Connecting to Hive server successful ...... ")

        try:
            for table_name in tables:
                all_pros = ",".join(tables[table_name])
                logger.info(f"Hive source: Reading data from table {table_name} ...... ")
                cur.execute(f"select {all_pros} from {table_name}")
                for value_tuple in cur.fetchall():
                    data = {name: value_tuple[num] for num, name in enumerate(tables[table_name])}
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=table_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
        except Exception as err:
            reason = "Hive source: Failed to read data"
            logger.error(reason)
            raise err
        finally:
            cur.close()
            conn.close()
