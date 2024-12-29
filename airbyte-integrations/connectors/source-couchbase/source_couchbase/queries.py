# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

from typing import Optional


def get_documents_query(bucket: str, scope: str, collection: str, cursor_field: str, cursor_value: Optional[int] = None) -> str:
    query = f"""
    SELECT META().id as _id, 
           lm as {cursor_field},
           *
    FROM `{bucket}`.`{scope}`.`{collection}`
    LET lm = TO_NUMBER(meta().xattrs.`$document`.last_modified)
    """

    if cursor_value is not None:
        query += f"\nWHERE lm > {cursor_value}"

    query += f"\nORDER BY lm ASC"
    return query


def get_max_cursor_value_query(bucket: str, scope: str, collection: str) -> str:
    return f"""
    SELECT MAX(TO_NUMBER(meta().xattrs.`$document`.last_modified)) as max_cursor_value
    FROM `{bucket}`.`{scope}`.`{collection}`
    """
