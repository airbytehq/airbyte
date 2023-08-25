#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from databend_sqlalchemy import connector


class DatabendClient:
    def __init__(self, host: str, port: int, database: str, table: str, username: str, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.database = database
        self.table = table
        self.username = username
        self.password = password

    def open(self):
        return connector.connect(f"https://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}").cursor()

