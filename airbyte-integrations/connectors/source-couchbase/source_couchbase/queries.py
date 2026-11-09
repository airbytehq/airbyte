# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

from typing import Optional


LAST_MODIFIED = "TO_NUMBER(META().xattrs.`$document`.last_modified)"


def get_documents_query(bucket: str, scope: str, collection: str, cursor_field: str, cursor_value: Optional[int] = None) -> str:
    # Documents are paged in primary-index (META().id) order using keyset pagination ($last_id / $page_size).
    # This lets the query service stream each page straight from the index instead of fetching and sorting the
    # whole collection in memory, which fails on large collections with "Query node has run out of memory" (5600)
    # and "Timeout exceeded" (1080) errors.
    query = f"""
    SELECT META().id AS _id,
           {LAST_MODIFIED} AS {cursor_field},
           *
    FROM `{bucket}`.`{scope}`.`{collection}`
    WHERE META().id > $last_id
    """

    if cursor_value is not None:
        query += f"\n      AND {LAST_MODIFIED} > {cursor_value}"

    query += "\n    ORDER BY META().id ASC\n    LIMIT $page_size"
    return query


def get_max_cursor_value_query(bucket: str, scope: str, collection: str) -> str:
    return f"""
    SELECT MAX({LAST_MODIFIED}) as max_cursor_value
    FROM `{bucket}`.`{scope}`.`{collection}`
    """
