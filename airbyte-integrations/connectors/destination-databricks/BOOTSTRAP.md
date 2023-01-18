# Databricks Lakehouse Destination Connector Bootstrap

This destination syncs data to Delta Lake on Databricks Lakehouse. It does so in two steps:

1. Persist source data in S3 staging files in the Parquet format, or in Azure blob storage staging files in the CSV format.
2. Create delta table based on the staging files.

See [this](https://docs.airbyte.io/integrations/destinations/databricks) link for the nuances about the connector.
