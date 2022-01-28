# BigQuery Destination Connector Bootstrap

BigQuery is a serverless, highly scalable, and cost-effective data warehouse
offered by Google Cloud Provider.

BigQuery connector is producing the standard Airbyte outputs using a `_airbyte_raw_*` tables storing the JSON blob data first. Afterward, these are transformed and normalized into separate tables, potentially "exploding" nested streams into their own tables if [basic normalization](https://docs.airbyte.io/understanding-airbyte/basic-normalization) is configured.

See [this](https://docs.airbyte.io/integrations/destinations/bigquery) link for more information about the connector.
