from dagster import MetadataValue, Output
import pandas as pd
from typing import NewType

OutputDataFrame = Output[pd.DataFrame]


def output_dataframe(result_df: pd.DataFrame) -> Output[pd.DataFrame]:
    """
    Returns a Dagster Output object with a dataframe as the result and a markdown preview.
    """
    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})
