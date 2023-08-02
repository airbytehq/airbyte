# BigQuery Denormalized Destination Connector Bootstrap

Instead of splitting the final data into multiple tables, this destination leverages BigQuery capabilities with [Structured and Repeated fields](https://cloud.google.com/bigquery/docs/nested-repeated) to produce a single "big" table per stream. This does not write the `_airbyte_raw_*` tables in the destination and normalization from this connector is not supported at this time.

See [this](https://docs.airbyte.io/integrations/destinations/databricks) link for the nuances about the connector.