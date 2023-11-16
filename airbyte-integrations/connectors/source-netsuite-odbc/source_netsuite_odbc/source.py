#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import json
from datetime import datetime
import hmac
import hashlib
import pyodbc
import time

import traceback
import random
import string

import base64
from typing import Dict, Generator, Mapping, Tuple, Union, Any

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source
from source_netsuite_odbc.discover_utils import NetsuiteODBCTableDiscoverer



class SourceNetsuiteOdbc(Source):
    logger: logging.Logger = logging.getLogger("airbyte")

    def generate_nonce(self) -> str:
        # Define the characters to choose from
        characters = string.ascii_letters + string.digits
        # Generate a random 10-character string
        random_string = ''.join(random.choice(characters) for i in range(10))
        return random_string
    
    def construct_password(self, config: Mapping[str, Any]) -> str:

        time_tuple = datetime.now().timetuple() 
        timestamp = str(time.mktime(time_tuple))[0:10]

        nonce = self.generate_nonce()

        base_string = config['realm'] + '&' + config['consumer_key'] + '&' + config['token_key'] + '&' + nonce + '&' + timestamp

        key = config['consumer_secret'] + '&' + config['token_secret']

        hmac_sha256 = hmac.new(key.encode(), base_string.encode(), hashlib.sha256)

        # Compute the HMAC and encode the result in Base64
        hmac_base64 = base64.b64encode(hmac_sha256.digest())

        hmac_base64_str = hmac_base64.decode()

        return base_string + '&' + hmac_base64_str + '&HMAC-SHA256'
    

    def create_database_cursor(self, config: Mapping[str, Any]) -> pyodbc.Cursor:
        password = self.construct_password(config)
        connection_string = f'DRIVER=NetSuite ODBC Drivers 8.1;Host={config["service_host"]};Port={config["service_port"]};Encrypted=1;AllowSinglePacketLogout=1;Truststore=/opt/netsuite/odbcclient/cert/ca3.cer;ServerDataSource=NetSuite2.com;UID=TBA;PWD={password};CustomProperties=AccountID={config["realm"]};RoleID=57;StaticSchema=1'
        cxn = pyodbc.connect(connection_string)
        return cxn.cursor()



    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            cursor = self.create_database_cursor(config)

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
            
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            print(e)

            traceback.print_exc() 
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """

        cursor = self.create_database_cursor(config)
        discoverer = NetsuiteODBCTableDiscoverer(cursor)
        streams = discoverer.get_streams()

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        stream_name = "TableName"  # Example
        data = {"columnName": "Hello World"}  # Example

        print('Running read!')
        print('Catalog')
        print(catalog)
        print(state)

        # Not Implemented

        yield AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
        )
