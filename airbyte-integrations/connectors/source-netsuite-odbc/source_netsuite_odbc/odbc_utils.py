# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import base64
import hashlib
import hmac
import random
import string
import time
from datetime import datetime
from typing import Any, Mapping

import pyodbc


class NetsuiteODBCCursorConstructor:
    def generate_nonce(self) -> str:
        # Define the characters to choose from
        characters = string.ascii_letters + string.digits
        # Generate a random 10-character string
        random_string = "".join(random.choice(characters) for i in range(10))
        return random_string

    def construct_password(self, config: Mapping[str, Any]) -> str:

        time_tuple = datetime.now().timetuple()
        timestamp = str(time.mktime(time_tuple))[0:10]

        nonce = self.generate_nonce()

        base_string = config["realm"] + "&" + config["consumer_key"] + "&" + config["token_key"] + "&" + nonce + "&" + timestamp

        key = config["consumer_secret"] + "&" + config["token_secret"]

        hmac_sha256 = hmac.new(key.encode(), base_string.encode(), hashlib.sha256)

        # Compute the HMAC and encode the result in Base64
        hmac_base64 = base64.b64encode(hmac_sha256.digest())

        hmac_base64_str = hmac_base64.decode()

        return base_string + "&" + hmac_base64_str + "&HMAC-SHA256"

    def create_database_cursor(self, config: Mapping[str, Any]) -> pyodbc.Cursor:
        password = self.construct_password(config)
        connection_string = f'DRIVER=NetSuite ODBC Drivers 8.1;Host={config["service_host"]};Port={config["service_port"]};Encrypted=1;AllowSinglePacketLogout=1;Truststore=/opt/netsuite/odbcclient/cert/ca3.cer;ServerDataSource=NetSuite2.com;UID=TBA;PWD={password};CustomProperties=AccountID={config["realm"]};RoleID=57;StaticSchema=1'
        cxn = pyodbc.connect(connection_string)
        return cxn.cursor()
