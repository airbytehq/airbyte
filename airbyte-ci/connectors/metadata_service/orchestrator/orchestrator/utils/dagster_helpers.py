from dagster import MetadataValue, Output

def OutputDataFrame(result_df):
    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})
