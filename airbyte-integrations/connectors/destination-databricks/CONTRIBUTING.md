# destination-databricks: Contributor notes

## Databricks JDBC driver

This connector requires a JDBC driver to connect to a Databricks cluster. Before using the driver, accept the Databricks JDBC/ODBC driver license: https://databricks.com/jdbc-odbc-driver-license.

## Test configuration

Integration tests require access to AWS S3, Azure Blob Storage, and a Databricks cluster.

If you're a community contributor:

1. Create a Databricks cluster.
2. Create an S3 bucket.
3. Create an Azure storage container.
4. Grant the Databricks cluster full access to the S3 bucket and Azure container, or mount the storage through DBFS.
5. Put the Databricks and S3 credentials in `sample_secrets/config.json`.
6. Put the Databricks and Azure credentials in `sample_secrets/azure_config.json`.
7. Rename `sample_secrets` to `secrets`.

If you're an Airbyte employee:

1. Get the `destination databricks creds` secret from LastPass.
2. Put it in `sample_secrets/config.json`.
3. Rename `sample_secrets` to `secrets`.
