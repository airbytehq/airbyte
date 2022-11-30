#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Dict, List

from airbyte_cdk.logger import AirbyteLogger
from firebolt.async_db import Connection as AsyncConnection
from firebolt.async_db import connect as async_connect
from firebolt.client import DEFAULT_API_URL
from firebolt.client.auth import UsernamePassword
from firebolt.db import Connection, connect


def parse_config(config: json, logger: AirbyteLogger) -> Dict[str, Any]:
    """
    Convert dict of config values to firebolt.db.Connection arguments

    :param config: json-compatible dict of settings
    :param logger: AirbyteLogger instance to print logs.

    :return: dictionary of firebolt.db.Connection-compatible kwargs
    """
    connection_args = {
        "database": config["database"],
        "auth": UsernamePassword(config["username"], config["password"]),
        "api_endpoint": config.get("host", DEFAULT_API_URL),
        "account_name": config.get("account"),
    }
    # engine can be a name or a full URL of a cluster
    engine = config.get("engine")
    if engine:
        if "." in engine:
            connection_args["engine_url"] = engine
        else:
            connection_args["engine_name"] = engine
    else:
        logger.info("Engine parameter was not provided. Connecting to the default engine.")
    return connection_args


def establish_connection(config: json, logger: AirbyteLogger) -> Connection:
    """
    Creates a connection to Firebolt database using the parameters provided.

    :param config: Json object containing db credentials.
    :param logger: AirbyteLogger instance to print logs.

    :return: PEP-249 compliant database Connection object.
    """
    logger.debug("Connecting to Firebolt.")
    connection = connect(**parse_config(config, logger))
    logger.debug("Connection to Firebolt established.")
    return connection


async def establish_async_connection(config: json, logger: AirbyteLogger) -> AsyncConnection:
    """
    Creates an async connection to Firebolt database using the parameters provided.
    This connection can be used for parallel operations.

    :param config: Json object containing db credentials.
    :param logger: AirbyteLogger instance to print logs.

    :return: PEP-249 compliant database Connection object.
    """
    logger.debug("Connecting to Firebolt.")
    connection = await async_connect(**parse_config(config, logger))
    logger.debug("Connection to Firebolt established.")
    return connection


async def get_firebolt_tables(connection: AsyncConnection) -> List[str]:
    """
    Fetch a list of tables that are compatible with Airbyte.
    Currently this includes Fact and Dimension tables

    :param connection: Connection object connected to a database

    :return: List of table names
    """
    query = """
    SELECT
        table_name
    FROM
        information_schema.tables
    WHERE
        "table_type" IN ('FACT', 'DIMENSION')
    """
    cursor = connection.cursor()
    await cursor.execute(query)
    return [table[0] for table in await cursor.fetchall()]
