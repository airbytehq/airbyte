from dagster import MetadataValue, Output
import pandas as pd
import hashlib
from typing import Optional, List

OutputDataFrame = Output[pd.DataFrame]
CURSOR_SEPARATOR = ":"


def output_dataframe(result_df: pd.DataFrame) -> Output[pd.DataFrame]:
    """
    Returns a Dagster Output object with a dataframe as the result and a markdown preview.
    """
    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})


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
