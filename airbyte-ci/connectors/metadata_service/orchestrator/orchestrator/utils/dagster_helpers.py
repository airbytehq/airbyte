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


def deserialize_composite_etags_cursor(etag_cursors: Optional[str]) -> List[str]:
    """Deserialize a cursor string into a list of etags.

    Args:
        etag_cursors (Optional[str]): A cursor string

    Returns:
        List[str]: A list of etags
    """
    return etag_cursors.split(CURSOR_SEPARATOR) if etag_cursors else []


def serialize_composite_etags_cursor(etags: List[str]) -> str:
    """Serialize a list of etags into a cursor string.

    Dagster cursors are strings, so we need to serialize the list of etags into a string.
    https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors#idempotence-and-cursors

    Args:
        etags (List[str]): unique etag ids from GCS

    Returns:
        str: A cursor string
    """
    return CURSOR_SEPARATOR.join(etags)
