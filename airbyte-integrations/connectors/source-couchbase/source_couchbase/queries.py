# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

from typing import Optional

def get_documents_query(bucket: str, scope: str, collection: str) -> str:
    return f"""
    SELECT META().id as _id, *
    FROM `{bucket}`.`{scope}`.`{collection}`
    """

def get_incremental_documents_query(bucket: str, scope: str, collection: str, cursor_value: Optional[int] = None) -> str:
    query = f"""
    SELECT META().id as _id, 
           to_number(meta().xattrs.`$document`.last_modified) as _ab_cdc_updated_at,
           *
    FROM `{bucket}`.`{scope}`.`{collection}`
    """
    
    if cursor_value:
        query += f"\nWHERE meta().xattrs.`$document`.last_modified > {cursor_value}"
    
    query += "\nORDER BY meta().xattrs.`$document`.last_modified ASC"
    return query
