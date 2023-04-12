from dagster import MetadataValue, Output
import pandas as pd
from typing import Optional, List

OutputDataFrame = Output[pd.DataFrame]
CURSOR_SEPARATOR = ":"


def output_dataframe(result_df: pd.DataFrame) -> Output[pd.DataFrame]:
    """
    Returns a Dagster Output object with a dataframe as the result and a markdown preview.
    """
    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})


def deserialize_composite_etag_cursor(etag_cursor: Optional[str]) -> List[str]:
    if etag_cursor is None:
        return []

    return etag_cursor.split(CURSOR_SEPARATOR)


def serialize_composite_etag_cursor(etags: List[str]):
    return CURSOR_SEPARATOR.join(etags)
