# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

def get_documents_query(bucket: str, scope: str, collection: str) -> str:
    return f"""
    SELECT META().id, *
    FROM `{bucket}`.`{scope}`.`{collection}`
    """

def get_incremental_documents_query(bucket: str, scope: str, collection: str, cursor_field: str, cursor_value: Optional[str] = None) -> str:
    query = f"""
    SELECT META().id, *
    FROM `{bucket}`.`{scope}`.`{collection}`
    """
    
    if cursor_value:
        query += f"\nWHERE {cursor_field} > '{cursor_value}'"
    
    query += f"\nORDER BY {cursor_field} ASC"
    return query
