#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from databend_sqlalchemy import connector


class DatabendClient:
    def __init__(self, host: str, port: int, database: str, table: str, username: str, password: str = None):
        self.host = host
        self.port = port
        self.database = database
        self.table = table
        self.username = username
        self.password = password

    def open(self):
        handle = connector.connect(f"https://{self.username}:{self.password}@{self.host}:{self.port}").cursor()

        return handle
