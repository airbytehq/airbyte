#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import hashlib
from typing import List, Optional

import pandas as pd
from dagster import MetadataValue, Output

OutputDataFrame = Output[pd.DataFrame]
CURSOR_SEPARATOR = ":"


def output_dataframe(result_df: pd.DataFrame) -> Output[pd.DataFrame]:
    """
    Returns a Dagster Output object with a dataframe as the result and a markdown preview.
    """

    # Truncate to 10 rows to avoid dagster throwing a "too large" error
    MAX_PREVIEW_ROWS = 10
    is_truncated = len(result_df) > MAX_PREVIEW_ROWS
    preview_result_df = result_df.head(MAX_PREVIEW_ROWS)

    return Output(
        result_df,
        metadata={"count": len(result_df), "preview": MetadataValue.md(preview_result_df.to_markdown()), "is_truncated": is_truncated},
    )


def string_array_to_hash(strings: List[str]) -> str:
    """Hash a list of strings into a cursor string.

    Args:
        unique_strings (List[str]): unique strings

    Returns:
        str: A cursor string
    """
    unique_strings = list(set(strings))
    unique_strings.sort()
    return hashlib.md5(str(unique_strings).encode("utf-8")).hexdigest()
