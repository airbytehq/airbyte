from dagster import MetadataValue, Output

def OutputDataFrame(result_df):
    """
    Returns a Dagster Output object with a dataframe as the result and a markdown preview.
    """
    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})
