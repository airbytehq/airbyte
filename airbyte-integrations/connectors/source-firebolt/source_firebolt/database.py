#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from firebolt.async_db import Connection as AsyncConnection
from firebolt.async_db import connect as async_connect
from firebolt.client import DEFAULT_API_URL
from firebolt.client.auth import Auth, ClientCredentials, UsernamePassword
from firebolt.db import Connection, connect


def _determine_auth(key: str, secret: str) -> Auth:
    """
    Determine between new auth based on key and secret or legacy email based auth.
    """
    if "@" in key:
        # email auth can only be used with UsernamePassword
        return UsernamePassword(key, secret)
    else:
        return ClientCredentials(key, secret)


def parse_config(config: json, logger: logging.Logger) -> Dict[str, Any]:
    """
    Convert dict of config values to firebolt.db.Connection arguments

    :param config: json-compatible dict of settings
    :param logger: logging.Logger instance to print logs.

    :return: dictionary of firebolt.db.Connection-compatible kwargs
    """
    # We should use client_id/client_secret, this code supports username/password for legacy users
    auth = _determine_auth(config.get("client_id", config.get("username")), config.get("client_secret", config.get("password")))
    connection_args = {
        "database": config["database"],
        "auth": auth,
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


def establish_connection(config: json, logger: logging.Logger) -> Connection:
    """
    Creates a connection to Firebolt database using the parameters provided.

    :param config: Json object containing db credentials.
    :param logger: logging.Logger instance to print logs.

    :return: PEP-249 compliant database Connection object.
    """
    logger.debug("Connecting to Firebolt.")
    connection = connect(**parse_config(config, logger))
    logger.debug("Connection to Firebolt established.")
    return connection


async def establish_async_connection(config: json, logger: logging.Logger) -> AsyncConnection:
    """
    Creates an async connection to Firebolt database using the parameters provided.
    This connection can be used for parallel operations.

    :param config: Json object containing db credentials.
    :param logger: logging.Logger instance to print logs.

    :return: PEP-249 compliant database Connection object.
    """
    logger.debug("Connecting to Firebolt.")
    connection = await async_connect(**parse_config(config, logger))
    logger.debug("Connection to Firebolt established.")
    return connection


def get_table_structure(connection: Connection) -> Dict[str, List[Tuple]]:
    """
    Get columns and their types for all the tables and views in the database.

    :param connection: Connection object connected to a database

    :return: Dictionary containing column list of each table
    """
    column_mapping = defaultdict(list)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT table_name, column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_name NOT IN (SELECT table_name FROM information_schema.tables WHERE table_type IN ('EXTERNAL', 'CATALOG'))"
    )
    for t_name, c_name, c_type, nullable in cursor.fetchall():
        column_mapping[t_name].append((c_name, c_type, nullable))
    cursor.close()
    return column_mapping
