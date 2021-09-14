# Databricks Destination Connector Bootstrap

The Databricks Connector enables a developer to sync data into a Databricks cluster. It does so in two steps:

1. Persist source data in S3 staging files in the Parquet format.
2. Create delta table based on the Parquet staging files.
