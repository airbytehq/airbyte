#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


class SqliteWriter:
    def __init__(self, path: str) -> None:
        self.path = path

    def delete_table(self, name: str):
        """
        Delete the resulting table.
        Primarily used in Overwrite strategy to clean up previous data.

        :param name: table name to delete
        """
        pass

    def create_raw_table(self, name: str):
        """
        Create the resulting _airbyte_raw table

        :param name: table name to create
        """
        pass

    def flush(self):
        pass
