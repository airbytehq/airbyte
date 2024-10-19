#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from databend_sqlalchemy import connector


class DatabendClient:
    def __init__(self, host: str, port: int, database: str, table: str, username: str, ssl: bool, password: str = None):
        self.host = host
        self.port = port
        self.database = database
        self.table = table
        self.username = username
        self.password = password
        self.ssl = ssl or False

    def open(self):
        if self.ssl:
            handle = connector.connect(
                f"https://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?secure={self.ssl}").cursor()
        else:
            handle = connector.connect(
                f"http://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}").cursor()

        return handle
