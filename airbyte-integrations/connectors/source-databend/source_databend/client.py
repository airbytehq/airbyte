#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from databend_sqlalchemy import connector
from collections import defaultdict
from typing import Dict, List, Tuple


def establish_conn(host: str, port: int, database: str, table: str, username: str, password: str = None):
    cursor = connector.connect(f"https://{username}:{password}@{host}:{port}").cursor()

    return cursor


def get_table_structure(cursor) -> Dict[str, List[Tuple]]:
    """
    Get columns and their types for all the tables and views in the database.
     :return: Dictionary containing column list of each table
    """
    column_mapping = defaultdict(list)
    cursor.execute(
        "SELECT table_name, column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_name NOT IN (SELECT table_name FROM information_schema.tables WHERE table_type IN ('EXTERNAL', 'CATALOG'))"
    )
    for t_name, c_name, c_type, nullable in cursor.fetchall():
        column_mapping[t_name].append((c_name, c_type, nullable))
    cursor.close()
    return column_mapping
