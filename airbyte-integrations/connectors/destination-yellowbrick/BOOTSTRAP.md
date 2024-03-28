# Yellowbrick Destination Connector Bootstrap

Yellowbrick is a highly efficient and elastically scalable data warehouse that runs on Kubernetes in all major public clouds and on-premises.

Yellowbrick connector produces the standard Airbyte outputs using `_airbyte_raw_*` tables storing the JSON blob data first. Afterward, these are transformed and normalized into separate tables, potentially "exploding" nested streams into their own tables if [basic normalization](https://docs.airbyte.io/understanding-airbyte/basic-normalization) is configured.

See [this](https://docs.airbyte.io/integrations/destinations/yellowbrick) link for more information about the connector.
